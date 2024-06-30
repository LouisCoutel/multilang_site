"""
ASGI config for multilang_site project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import logging
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multilang_site.settings')
logging.warning(os.getenv('DJANGO_SETTINGS_MODULE'))

#fmt: off
from django.core.asgi import get_asgi_application
#fmt: on

django_asgi_app = get_asgi_application()


#fmt: off
from channels.routing import ProtocolTypeRouter, URLRouter
from main.routing import websocket_urlpatterns
#fmt: on

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
