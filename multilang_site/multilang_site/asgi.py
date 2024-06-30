"""
ASGI config for multilang_site project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter
import os

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multilang_site.settings')


#fmt: off
from main.routing import websocket_urlpatterns
#fmt: on

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
