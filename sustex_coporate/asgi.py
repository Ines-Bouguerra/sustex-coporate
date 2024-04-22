"""
ASGI config for sustex_coporate project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import os
from django.core.asgi import get_asgi_application
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustex_coporate.settings')
django.setup()
from sustex_coporate.urls import websocket_urlpatterns
application=ProtocolTypeRouter(
    {   'http':get_asgi_application(),
        'websocket': AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
# application = get_asgi_application()
