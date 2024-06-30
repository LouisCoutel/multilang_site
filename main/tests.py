""" Test suites """

from django.db.models import QuerySet
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from django.test.client import Client, json
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from main.consumers.assistant_consumer import AssistantConsumer
from main.assistant_utils import create_assistant, distance_search, get_embedding
from main.models import Article


def create_dummy_article():
    """ Utility to quickly create a dummy article. """

    title = "MOTIVATION !"
    content = "motivation"
    emb = get_embedding(title + " " + content)

    Article.objects.create(
        title=title, title_fr=title, content=content, content_fr=content, embedding=emb)


class AssistantTests(TestCase):
    """ Test suite for assistant utils and websocket interactions with the AI assistant. """

    async def test_ws(self):
        """ Check connecting, sending and receiving messages through websocket. """

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

    def test_create_assistant(self):
        a, t = create_assistant('fr')

        assert isinstance(a, Assistant)
        assert isinstance(t, Thread)

    def test_create_embedding(self):
        """ Check embedding dimensions. """

        emb = get_embedding("Bonjour")
        assert isinstance(emb, list)
        assert len(emb) == 1536

    def test_distance_search(self):
        create_dummy_article()
        res = distance_search("Motivation")

        assert isinstance(res, QuerySet)
        assert len(res) > 0
        assert res.first().title == "MOTIVATION !"


class ArticlesTests(TestCase):
    """ Suite for article views. """

    def setUp(self) -> None:
        self.c = Client()

    def test_get_article(self):
        create_dummy_article()

        headers = {'HTTP_HX-Request': 'true'}
        res = self.c.get("/article/?id=1", **headers, follow=True)

        self.assertTemplateUsed(res, "main/articles/article.html")

    def test_get_articles(self):
        create_dummy_article()

        headers = {'HTTP_HX-Request': 'true'}
        res = self.c.get("/articles/?page=1", **headers, follow=True)

        self.assertTemplateUsed(res, "main/articles/articles.html")

    def test_search_articles(self):
        create_dummy_article()
        headers = {'HTTP_HX-Request': 'true'}

        res = self.c.get("/search/?query=motivation", **headers, follow=True)

        self.assertTemplateUsed(res, "main/articles/articles.html")
