from itertools import chain

from pyasn1_modules.rfc2315 import data

from dj_notif.models import BaseNotificationModel, AbstractBaseNotificationModel, BaseBroadcastNotificationModel


class AbstractNotificationManager:
    def __init__(self):
        self.user = None

    @staticmethod
    def get_notification_models():
        return {model.notification_class_name: model for model in AbstractBaseNotificationModel.get_all_subclasses()}

    def get_notification_categories(self):
        return list(self.get_notification_models().keys())

    def get_notifications(self, broadcast=False):
        all_qs = []

        for cls in self.get_notification_models().values():
            if broadcast:
                qs = cls.objects.all()
            else:
                qs = cls.objects.filter(user=self.user)

            all_qs.append(qs)

        # Combine all querysets into one iterable
        combined = chain(*all_qs)

        # Sort by created_at (assuming it's in your BaseModel)
        sorted_notifications = sorted(combined, key=lambda n: n.created_at, reverse=True)

        return sorted_notifications


class NotificationManager(AbstractNotificationManager):
    def __init__(self, user):
        super().__init__()
        self.user = user

    @staticmethod
    def get_notification_models():
        return {model.notification_class_name: model for model in BaseNotificationModel.get_all_subclasses()}

    def get_categories_unread_count(self):
        notifications = self.get_categorized_notifications()
        return {notif_cls_name: notif_qs.filter(read_at=None).count() for
                notif_cls_name, notif_qs in notifications.items()}

    def get_notifications_serialized(self, unread_only=False):
        notifications_query = self.get_notifications()
        if unread_only:
            notifications_query = list(filter(lambda x: not x.read_at, notifications_query))
        return [x.__class__.get_serializer_class()(x).data for x in notifications_query]

    def get_categorized_notifications(self, unread_only=False):
        data = {}
        for cls_name, cls in self.get_notification_models().items():
            if not unread_only:
                data[cls_name] = cls.objects.filter(user=self.user)
            else:
                data[cls_name] = cls.objects.filter(user=self.user, read_at=None)
        return data

    def get_categorized_notifications_serialized(self, unread_only=False):
        user_notifications = self.get_categorized_notifications(unread_only=unread_only)
        serialized_notifications = {
            notif_cls_name: notif_qs.model.get_serializer_class()(
                notif_qs,
                many=True,
                excluded_fields=['category'],
                context={'unread_queryset': notif_qs.filter(read_at=None)}).data
            for notif_cls_name, notif_qs in user_notifications.items()}
        return serialized_notifications

    def get_category_notifications(self, category, unread_only=False):
        model = self.get_notification_models().get(category)
        if not unread_only:
            return model.objects.filter(user=self.user).prefetch_related('user')
        else:
            return model.objects.filter(user=self.user, read_at=None).prefetch_related('user')

    def get_category_notifications_serialized(self, category, unread_only=False):
        model = self.get_notification_models().get(category)
        notifications = self.get_category_notifications(category, unread_only=unread_only)
        return model.get_serializer_class()(notifications, many=True, excluded_fields=['category'],
                                            context={'unread_queryset': notifications.filter(read_at=None)}).data


class BroadcastNotificationManager(AbstractNotificationManager):
    @staticmethod
    def get_notification_models():
        return {model.notification_class_name: model for model in BaseBroadcastNotificationModel.get_all_subclasses()}

    def get_notifications_serialized(self, requested_user=None):
        notifications_query = self.get_notifications(broadcast=True)
        return [x.__class__.get_serializer_class()(x, context={'user': requested_user}).data for x in
                notifications_query]

    def get_categorized_notifications(self):
        data = {}
        for cls_name, cls in self.get_notification_models().items():
            data[cls_name] = cls.objects.all()
        return data

    def get_categorized_notifications_serialized(self, requested_user=None):
        user_notifications = self.get_categorized_notifications()

        serialized_notifications = {
            notif_cls_name: notif_qs.model.get_serializer_class()(
                notif_qs.order_by('-created_at'), many=True, excluded_fields=['category'],
                context={'user': requested_user}).data
            for notif_cls_name, notif_qs in user_notifications.items()}
        return serialized_notifications

    def get_category_notifications(self, category):
        model = self.get_notification_models().get(category)
        return model.objects.all()

    def get_category_notifications_serialized(self, category, requested_user=None):
        model = self.get_notification_models().get(category)
        serializer_class = model.get_serializer_class()
        notifications = model.objects.all().order_by('-created_at')

        return serializer_class(notifications, many=True, excluded_fields=['category'],
                                context={'user': requested_user}).data
