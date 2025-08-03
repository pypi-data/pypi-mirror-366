import logging
import json
from dj_notif.base.consumers import BaseConsumer
from dj_notif.utils.main import MessageResult
from dj_notif.utils.async_funcs import get_notifications, mark_as_read, mark_all_as_read

logger = logging.getLogger('notification')


class NotificationConsumer(BaseConsumer):
    NotificationTypesActionsMap = {
        "notifications": {
            1: "get",
            2: "mark_as_read",
            3: "mark_all_as_read"
        }
    }

    # def get_serializer_class(self, action_type, action_name):
    #     from serializers import BaseNotificationConsumerSerializer
    #     exists_serializers = BaseNotificationConsumerSerializer.__subclasses__()

    async def handle_action(self, action_type, action_name, payload):
        match (action_type, action_name):

            # TODO future update: serializer for ws notification manager
            # case ('notifications', 'get'):
            #     project_id = payload.get("project_id")  # NOT REQUIRED, FILTER
            #     task_id = payload.get("task_id")  # NOT REQUIRED, FILTER
            #     result = await get_notifications(self.user, project_id, task_id)
            #     await self.send_response(action_type, action_name, result)
            #
            # case ('notifications', 'mark_as_read'):
            #     notification_id = payload.get('notification_id')  # REQUIRED
            #     result = await mark_as_read(self.user, notification_id)
            #     await self.send_response(action_type, action_name, result)
            #
            # case ('notifications', 'mark_all_as_read'):
            #     project_id = payload.get("project_id")  # NOT REQUIRED, FILTER
            #     task_id = payload.get("task_id")  # NOT REQUIRED, FILTER
            #     result = await mark_all_as_read(self.user, project_id, task_id)
            #     await self.send_response(action_type, action_name, result)

            case _:
                logger.error(f"Unknown action_type: {action_type} or action_name: {action_name}")
                result = MessageResult("Unknown action", False, 404)
                await self.send_response(action_type, action_name, result)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    async def notifications(self, event):
        await self.send(text_data=json.dumps(event))
