from rest_framework import serializers

from dj_notif.base.serializers import BaseSerializer
from dj_notif.utils.main import get_subclasses


class AbstractBaseNotificationSerializer(BaseSerializer):
    user = None
    notification_class_name = None
    category = serializers.SerializerMethodField()

    def __new__(cls, *args, **kwargs):
        if not (_ := getattr(cls, "notification_class_name", None)):
            raise serializers.ValidationError("Define notification_class_name in child class attributes")
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):

        meta = self.Meta
        if not hasattr(meta, "fields"):
            meta.fields = ['id', 'category', 'title', 'description', 'level', 'created_at', 'read_at']

        if extra_fields := getattr(meta, "extra_fields", None):
            meta.fields.extend(extra_fields)

        super().__init__(*args, **kwargs)

    @classmethod
    def get_all_subclasses(cls):
        return get_subclasses(cls, recursive=True)

    @classmethod
    def _get_subclasses(cls) -> dict:
        all_subclasses = cls.get_all_subclasses()
        return {x.notification_class_name: x for x in all_subclasses}

    @classmethod
    def get_subclass(cls, notif_name):
        try:
            return cls._get_subclasses().get(notif_name)
        except Exception as err:
            raise serializers.ValidationError(err)

    def get_category(self, obj):
        return self.notification_class_name


class BaseNotificationSerializer(AbstractBaseNotificationSerializer):
    ...


class BaseBroadcastNotificationSerializer(AbstractBaseNotificationSerializer):
    read_at = serializers.SerializerMethodField()

    def get_read_at(self, obj):
        if request := self.context.get('request', None):
            user = request.user
            return obj.user_read_at_receipts.get(str(user.id), None)

        elif user := self.context.get('user', None):
            return obj.user_read_at_receipts.get(str(user.id), None)

        return None


# TODO future update: serializer for ws notification manager
# class BaseNotificationConsumerSerializer(serializers.Serializer):
#
#     def validate_action(self, action_name: str, action_type: str):
#         ...
#
#     def __init__(self, action_type: str, action_name: str):
#         self.type = action_type
#         self.action = action_name
#         super().__init__()
#
#
# class NotificationGetSerializer(BaseNotificationConsumerSerializer):
#     ...
#
#
# class NotificationMarkAsReadSerializer(BaseNotificationConsumerSerializer):
#     ...
#
#
# class NotificationMarkAllAsReadSerializer(BaseNotificationConsumerSerializer):
#     ...
