from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import models
from django.utils import timezone

from dj_notif.base.models import BaseModel
from dj_notif.utils.main import get_subclasses


class MethodNotAllowed(Exception):
    def __init__(self, method_name):
        self.method_name = method_name
        super().__init__(self.method_name)

    def __str__(self):
        return f"Method {self.method_name} not allowed in {self.__class__.__name__}"


class AbstractBaseNotificationModel(BaseModel):
    class NotificationLevel(models.IntegerChoices):
        low = 1,
        medium = 2,
        high = 3

    notification_class_name = None
    requested_user = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=50)
    level = models.IntegerField(choices=NotificationLevel.choices)
    description = models.CharField(max_length=200)

    def __new__(cls, *args, **kwargs):
        if not (_ := getattr(cls, "notification_class_name", None)):
            raise RuntimeError("Define notification_class_name in class attributes")
        return super().__new__(cls)

    class Meta:
        abstract = True

    @classmethod
    def get_all_subclasses(cls):
        return get_subclasses(cls, recursive=True)

    @classmethod
    def get_serializer_class(cls):
        from .serializers import AbstractBaseNotificationSerializer
        return AbstractBaseNotificationSerializer.get_subclass(cls.notification_class_name)

    def dispatch(self, broadcast=False):
        message_prefix = "Broadcast" if broadcast else "New"
        serializer = self.get_serializer_class()(self, excluded_fields=['user'])
        channel_layer = get_channel_layer()
        channel_name = self.get_channel_name()

        async_to_sync(channel_layer.group_send)(
            channel_name,  # This should match the group your WebSocket consumer is listening to
            {
                'type': 'notifications',  # This should match the method name in your WebSocket consumer
                'message': f'{message_prefix} Notification',
                'action': self.__class__.__name__,
                'payload': {
                    'notification': serializer.data
                }
            }
        )

    def get_channel_name(self):
        pass


class BaseNotificationModel(AbstractBaseNotificationModel):
    user = models.PositiveIntegerField()
    read_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        abstract = True

    @classmethod
    def create_notifications(cls, title: str, description: str, level: int, users: list[int]):
        for user_id in users:
            try:
                cls.objects.create(title=title, description=description, level=level, user=user_id)
            except Exception as err:
                print(err)
        return None

    def get_user_id(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if isinstance(self.user, User):
            return self.user.id
        else:
            return self.user

    def get_channel_name(self):
        return f"notif_user_{self.get_user_id()}"

    def save(self, *args, **kwargs):
        super(BaseNotificationModel, self).save(*args, **kwargs)
        self.dispatch()

    def __str__(self):
        return f"user_id:{self.get_user_id()}, title:{self.title}"


class BaseBroadcastNotificationModel(AbstractBaseNotificationModel):
    class NotificationTitle(models.TextChoices):
        system = 'system_notification'
        admin = 'admin_notification'

    title = models.CharField(choices=NotificationTitle.choices, max_length=50, default=NotificationTitle.system)
    user_read_at_receipts = models.JSONField(default=dict, null=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def get_serializer_class(cls):
        from .serializers import BaseBroadcastNotificationSerializer
        return BaseBroadcastNotificationSerializer.get_subclass(cls.notification_class_name)

    def mark_as_read(self, user_id):
        if not self.user_read_at_receipts:
            self.user_read_at_receipts = {}

        if exists_user_read_at_receipt := self.user_read_at_receipts.get(user_id, None):
            print(f"notification already marked as read at receipt: {exists_user_read_at_receipt}")
            return False
        self.user_read_at_receipts[str(user_id)] = timezone.localtime()
        self.save(update_fields=['user_read_at_receipts'])
        print(f"notification marked as read for user {user_id} at {self.user_read_at_receipts.get(str(user_id))}")
        return True

    def get_read_at(self, user_id: str):
        if exists_user_read_at_receipt := self.user_read_at_receipts.get(user_id, None):
            return exists_user_read_at_receipt

        return None

    def save(self, *args, **kwargs):
        super(BaseBroadcastNotificationModel, self).save(*args, **kwargs)
        self.dispatch(broadcast=True)

    def get_channel_name(self):
        return "broadcast"

    def __str__(self):
        return f"broadcast message from user {self.requested_user}"
