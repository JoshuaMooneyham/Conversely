from django.urls import path
from app.consumer import Consumer

# the empty string routes to ChatConsumer, which manages the chat functionality.
# websocket_urlpatterns = [
#     path("", ChatConsumer.as_asgi()),
# ]
websocket_urlpatterns = [
    path("ws/group/<group_name>", Consumer.as_asgi())
]