import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync, sync_to_async
from app.models import *

class Consumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user'] # grabs logged in user from scope
        self.group_name = self.scope['url_route']['kwargs']['group_name'] # grabs group name from url
        self.group = get_object_or_404(Group, name=self.group_name)
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data):
        json_data = json.loads(text_data) # Convert text to python object
        message = Message.objects.create(text=json_data['text'], user=self.user, group=self.group)
        event = {'type': 'message_handler', 'message_id': message.pk}
        async_to_sync(self.channel_layer.group_send)(self.group_name, event)

    def message_handler(self, event):
        html = render_to_string('message_partial.html', context={'message': Message.objects.get(pk=event['message_id']), 'user': self.user})
        self.send(text_data=html)

# class Consumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope['user']
#         self.group_name = self.scope['url_route']['kwargs']['group_name']
#         self.room_group_name = 'chat_%s' % self.group_name
#         self.group = sync_to_async(Group.objects.get)(name=self.group_name)

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         json_data = json.loads(text_data) # Convert text to python object
#         message = Message.objects.create(text=json_data['text'], user=self.user, group=self.group)
#         event = {'type': 'sendMessage', 'message_id': message.pk}
#         await self.channel_layer.group_send(self.room_group_name, event)

#     async def sendMessage(self, event):
#         html = render_to_string('message_partial.html', context={'message': Message.objects.get(pk=event['message_id']), 'user': self.user})
#         await self.send(text_data=html)

