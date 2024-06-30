# chat/routing.py
from django.urls import path
from main.consumers.assistant_consumer import AssistantConsumer


websocket_urlpatterns = [
    path("chat/assistant/", AssistantConsumer.as_asgi()),
]
