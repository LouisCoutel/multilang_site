from django.test import TestCase
from channels.testing import WebsocketCommunicator
from django.test.client import json
from main.consumers.assistant_consumer import AssistantConsumer
# Create your tests here.


class AssistantTests(TestCase):
    databases = '__all__'

    async def test_init(self):
        """ Check if assistant initialized properly and IDs are in session. """
        communicator = WebsocketCommunicator(
            AssistantConsumer.as_asgi(), "GET", "/chat/assistant/")
        connected, subprotocol = await communicator.connect()
        assert connected

        await communicator.send_to(text_data=json.dumps({"user-input": "test"}))
        message = await communicator.receive_from(timeout=5)
        print(message)
        assert 'msg assistant' in message
        await communicator.disconnect()


def test_redirect(self):
    """ Check if assistant view redirects to localized view."""

    res = self.client.get("/chat/")

    self.assertRedirects(res, expected_url="/en/chat/",
                         target_status_code=200)
