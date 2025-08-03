import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BaseConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.group_name = None
        self.user = None
        self.logger = None
        super().__init__(*args, **kwargs)

    async def connect(self, **kwargs):
        self.user = self.scope.get('user')

        if self.user and self.channel_layer:

            self.group_name = f"notif_user_{self.user.id}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add('broadcast', self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.group_name and self.channel_layer:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            action_type = data.get('type')
            action_name = data.get('action')
            payload = data.get("payload", {})

            self.logger.debug(f"Received action: {action_type} - {action_name} with payload: {payload}")

            # Handle the action based on its type using match-case
            await self.handle_action(action_type, action_name, payload)

        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format received.")
        except Exception as e:
            self.logger.exception(f"Error processing WebSocket message: {str(e)}")

    async def handle_action(self, action_type, action_name, payload):
        ...

    async def send_response(self, action_type, action_name, result):
        message_type = "result" if result.success else "error"

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': action_type,
                'action': action_name,
                'message': f'Action received: {action_name}',
                'payload': {
                    "status_code": result.status,
                    "success": result.success,
                    message_type: result.__str__(),
                    "meta_data": result.meta
                }
            }
        )

