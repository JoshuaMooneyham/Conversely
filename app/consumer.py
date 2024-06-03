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

        if self.user not in self.group.users_online.all():
            self.group.users_online.add(self.user)
            self.update_online_count()

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

        if self.user in self.group.users_online.all():
            self.group.users_online.remove(self.user)
            self.update_online_count()

    def receive(self, text_data):
        json_data = json.loads(text_data) # Convert text to python object
        message = Message.objects.create(text=json_data['text'], user=self.user, group=self.group)
        event = {'type': 'message_handler', 'message_id': message.pk}
        async_to_sync(self.channel_layer.group_send)(self.group_name, event)

    def message_handler(self, event):
        html = render_to_string('partials/message_send_partial.html', context={'message': Message.objects.get(pk=event['message_id']), 'user': self.user, 'channel': self.group_name})
        self.send(text_data=html)

    def delete_message(self, event):
        try:
            message = Message.objects.get(pk=event['message_id'])
            message.delete()
        except:
            pass
        html = render_to_string('partials/message_delete_partial.html', context={'message_id': event['message_id']})
        self.send(text_data=html)

    def update_message(self, event):
        message = Message.objects.get(pk=event['message_id'])
        message.text = event['text']
        message.save()
        html = render_to_string('message.html', context={'message': message, "user": self.user, "channel": self.group_name})
        self.send(text_data=html)

    def update_online_count(self):
        users_online = [i.username for i in self.group.users_online.all()]
        print(f'HIiiiiiiii {users_online}')
        online_count = self.group.users_online.count()
        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        async_to_sync(self.channel_layer.group_send)(self.group_name, event)

    def online_count_handler(self, event):
        online_count = event['online_count']

        html = render_to_string("partials/online_count.html", {'online_count':online_count})
        self.send(text_data=html)

    def ban_user(self, event):
        try:
            user = User.objects.get(pk=event['user_id'])
            if (user in self.group.banned_users.all()) == False:
                self.group.banned_users.add(user)
                self.group.save()
                print(self.group, user, self.user)
            if user in self.group.users.all():
                self.group.users.remove(user)
                self.group.save()
            html = render_to_string("partials/ban_partial.html", {'found_user': user, 'user': self.user, 'group': self.group.name})
            self.send(text_data=html)
        except:
            pass

    def unban_user(self, event):
        try:
            user = User.objects.get(pk=event['user_id'])
            if user in self.group.banned_users.all():
                self.group.banned_users.remove(user)
                self.group.save()
            html = render_to_string("partials/unban_partial.html", {'found_user': user, 'user': self.user, 'group': self.group.name})
            self.send(text_data=html)
        except: 
            pass

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

