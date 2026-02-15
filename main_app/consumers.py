import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We can handle authentication here if needed
        # For now, let's just accept all connections
        self.user = self.scope.get("user")
        if self.user and self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            await self.send(text_data=json.dumps({
                "type": "connection_established",
                "message": "Successfully connected to Mediguard Cloud"
            }))
        else:
            # For testing purposes, let's allow anonymous connections too
            # or you can reject them: await self.close()
            self.room_group_name = "anonymous"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            await self.send(text_data=json.dumps({
                "type": "connection_established",
                "message": "Successfully connected to Mediguard Cloud"
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"WebSocket RECEIVED: {text_data[:100]}...")
        data = json.loads(text_data)
        action = data.get("action")

        if action == "sync":
            await self.handle_sync(data)
        else:
            message = data.get("message")
            # Echo the message back or handle it
            await self.send(text_data=json.dumps({
                "type": "echo",
                "message": f"Echo: {message}"
            }))

    async def handle_sync(self, data):
        if not self.user or not self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                "type": "sync_error",
                "message": "Authentication required for sync"
            }))
            return

        from accounts.sync_utils import perform_sync
        from asgiref.sync import sync_to_async

        def progress_callback(status, progress, entity=None, current=None, total=None, mode=None):
            import asyncio
            from asgiref.sync import async_to_sync
            
            # This callback is called from within a sync context (perform_sync)
            # but we need to send data via the async channel layer
            async_to_sync(self.send)(text_data=json.dumps({
                "type": "sync_progress",
                "status": status,
                "progress": progress,
                "entity": entity,
                "current": current,
                "total": total,
                "mode": mode
            }))

        def item_success_callback(entity, instance, data):
             import asyncio
             from asgiref.sync import async_to_sync
             from django.core.serializers.json import DjangoJSONEncoder
             
             async_to_sync(self.send)(text_data=json.dumps({
                 "type": "sync_item_success",
                 "entity": entity,
                 "id": str(instance.id),
                 "new_data": data
             }, cls=DjangoJSONEncoder))

        try:
            # Run the sync logic in a separate thread because it's blocking DB work
            result = await sync_to_async(perform_sync)(
                self.user, 
                data, 
                progress_callback=progress_callback,
                item_success_callback=item_success_callback
            )
            
            from django.core.serializers.json import DjangoJSONEncoder
            await self.send(text_data=json.dumps({
                "type": "sync_complete",
                "result": result
            }, cls=DjangoJSONEncoder))
        except Exception as e:
            import traceback
            traceback.print_exc()
            await self.send(text_data=json.dumps({
                "type": "sync_error",
                "message": str(e)
            }))

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
