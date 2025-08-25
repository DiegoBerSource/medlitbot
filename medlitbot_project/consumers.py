"""
WebSocket consumers for real-time training updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from classification.models import TrainingJob, MLModel


class TrainingProgressConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for individual model training progress"""
    
    async def connect(self):
        self.model_id = self.scope['url_route']['kwargs']['model_id']
        self.room_group_name = f'training_{self.model_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages (if needed)
        pass

    # Receive message from room group
    async def training_update(self, event):
        """Send training update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'training_progress',
            'data': event['data']
        }))


class GlobalTrainingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for all training updates"""
    
    async def connect(self):
        self.room_group_name = 'global_training'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def training_update(self, event):
        """Send training update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'training_progress',
            'data': event['data']
        }))
