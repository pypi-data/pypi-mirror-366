from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_notif.managers import NotificationManager, BroadcastNotificationManager


class BaseNotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _parse_flags(request):
        unread_only = request.query_params.get('unread_only', '').lower() == 'true'
        categorized = request.query_params.get('categorized', '').lower() == 'true'
        page = request.query_params.get('page', 1)
        return unread_only, categorized, page


class UserNotificationViewSet(BaseNotificationViewSet):

    def list(self, request):
        unread_only, categorized, _ = self._parse_flags(request)
        manager = NotificationManager(user=request.user)

        if categorized:
            serialized = manager.get_categorized_notifications_serialized(unread_only=unread_only)
        else:
            serialized = manager.get_notifications_serialized(unread_only=unread_only)

        return Response(serialized)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        manager = NotificationManager(user=request.user)
        result = manager.get_categories_unread_count()
        return Response(result)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        manager = NotificationManager(user=request.user)
        total_updated = sum(
            model.objects.filter(user=request.user, read_at=None)
            .update(read_at=timezone.localtime())
            for model in manager.get_notification_models().values()
        )
        return Response({"detail": f"{total_updated} notifications marked as read."})

    @action(detail=False, methods=['get'], url_path='category/(?P<category>[^/.]+)')
    def category_notifications(self, request, category=None):
        unread_only, _, _ = self._parse_flags(request)
        manager = NotificationManager(user=request.user)
        categories = manager.get_notification_categories()

        if category not in categories:
            return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serialized = manager.get_category_notifications_serialized(category, unread_only=unread_only)
        return Response(serialized)

    @action(detail=False, methods=['post'], url_path='category/(?P<category>[^/.]+)/mark_all_read')
    def mark_category_read(self, request, category=None):
        manager = NotificationManager(user=request.user)
        if category not in manager.get_notification_categories():
            return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        model = manager.get_notification_models()[category]
        updated = model.objects.filter(user=request.user, read_at=None).update(read_at=timezone.localtime())

        return Response({"detail": f"{updated} notifications marked as read."})

    @action(detail=False, methods=['post'], url_path='category/(?P<category>[^/.]+)/mark_read/(?P<notification_id>\d+)')
    def mark_single_notification_read(self, request, category=None, notification_id=None):
        manager = NotificationManager(user=request.user)
        try:
            notif = manager.get_notification_models()[category].objects.get(id=notification_id, read_at=None)
            notif.read_at = timezone.localtime()
            notif.save(update_fields=['read_at'])
            return Response({'detail': f"Notification {notification_id} marked as read"})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)


class BroadcastNotificationViewSet(BaseNotificationViewSet):

    def list(self, request):
        unread_only, categorized, _ = self._parse_flags(request)
        manager = BroadcastNotificationManager()

        if categorized:
            serialized = manager.get_categorized_notifications_serialized(requested_user=request.user)
        else:
            serialized = manager.get_notifications_serialized(requested_user=request.user)

        return Response(serialized)

    @action(detail=False, methods=['get'], url_path='category/(?P<category>[^/.]+)')
    def get(self, request, category=None):
        manager = BroadcastNotificationManager()
        categories = manager.get_notification_categories()

        if category not in categories:
            return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serialized = manager.get_category_notifications_serialized(category, requested_user=request.user)
        return Response(serialized)

    @action(detail=False, methods=['post'], url_path='category/(?P<category>[^/.]+)/mark_read/(?P<notification_id>\d+)')
    def mark_single_notification_read(self, request, category=None, notification_id=None):
        manager = BroadcastNotificationManager()
        user_id = str(request.user.id)
        try:
            notif = manager.get_notification_models()[category].objects.filter(
                Q(**{f"user_read_at_receipts__{'16'}": False}) |
                ~Q(**{f"user_read_at_receipts__has_key": "16"}),
                id=notification_id
            ).get()

            formatted_time = timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')
            notif.user_read_at_receipts[user_id] = formatted_time
            notif.save(update_fields=['user_read_at_receipts'])
            return Response({'detail': f"Notification {notification_id} marked as read"})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
