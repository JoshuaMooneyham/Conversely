"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter , URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

default_application = get_asgi_application() # Initializes app / handles HTTP Requests

from app import routing

application = ProtocolTypeRouter( # Handles Websockets
    {
        "http" : default_application , 
        "websocket" : AllowedHostsOriginValidator( # Only allows connections from URLs listed in 'ALLOWED_HOSTS'
            AuthMiddlewareStack( # Uses django's auth middleware to give access to the logged in user
                URLRouter( # links the URL to the consumer
                    routing.websocket_urlpatterns
                )  
            )  
        )
    }
)
