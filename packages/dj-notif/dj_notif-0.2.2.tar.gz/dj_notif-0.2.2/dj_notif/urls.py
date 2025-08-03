from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dj_notif.views import UserNotificationViewSet, BroadcastNotificationViewSet
from django_channels_jwt.views import AsgiValidateTokenView

router = DefaultRouter()
router.register(r'user', UserNotificationViewSet, basename='user-notifications')
router.register(r'broadcast', BroadcastNotificationViewSet, basename='broadcast-notifications')

urlpatterns = [
    path("notifications/ws_auth/", AsgiValidateTokenView.as_view()),  # WS Authentication
    path('notifications/', include(router.urls)),
]
