""" Various utility functions for using and interacting with an OpenAI assistant"""

from typing import Tuple
from django.db.models import QuerySet
from django.utils.html import json
from openai import OpenAI
from pgvector.django import CosineDistance
from main.models import Article

client = OpenAI()


def create_assistant(lang) -> Tuple:
    """ Create an OpenAI assistant and set its id in session for retrieval.

    Args:
        lang (str): current language code.
    Returns:
        assistant, thread (tuple): assistant and thread instances packed in a tuple.
    """

    assistant = client.beta.assistants.create(
        name="BlogAssistant",
        description="You are an assistant for a blog platform. \
            You can help users write blog posts, you can also perform searches and return existing articles from the database.",
        instructions=f"Answer in the language corresponding to this code : {lang} unless asked to switch. \
            Keep answers short and to the point. \
            Format your response in markdown. Don't use headings larger than h5. \
            Introduce yourself to the user and explain what you can do.",
        tools=[{"type": "function",
                "function": {
                    "name": "distance_search",
                    "description": "Perform a search based on an article description in a vector database, \
                    go over the resulting objects and create a list of articles including either the 'title' or 'title_fr' field, \
                    depending on the language the request was made in. \
                    Use the provided 'relative_url' to point to the article page, don't prefix it but include the first slash. \
                    Use the provided content of each article to provide the user with a description. \
                    Ask the user if they are happy with the results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_request": {
                                "type": "string", "description": "The description of the kind of article the user is looking for."},
                        },
                        "required": ["user_request"]
                    }}},
               ],
        model="gpt-4o",
    )

    thread = client.beta.threads.create()

    return (assistant, thread)


def get_embedding(text: str, model="text-embedding-3-small"):
    """ Generate embedding using OpenAI API.

    Args:
        text(str): text to generate an embedding for .
        model(str): name of OpenAI model to use.

    Returns:
        vector embedding
    """

    text = text.replace("\n", " ")

    return client.embeddings.create(input=[text], model=model).data[0].embedding


def distance_search(article_desc: str) -> QuerySet:
    """ Run a similarity search in database with provided article description.

    Args:
        article_desc(str): user input describing what they want.

    Returns:
        matching_articles (QuerySet): articles that best match the provided description/request.
    """

    embedding = get_embedding(article_desc, model='text-embedding-3-small')

    matching_articles = Article.objects.annotate(
        distance=CosineDistance("embedding", embedding)
    ).order_by("distance")

    return matching_articles


def process_req_action(event) -> list:
    """ Trigger search on event, generate tool outputs.

        Args:
            event: current OpenAI event object. 

        Returns:
            tool_outputs (list): JSON formatted outputs of called functions. """

    tool_outputs = []

    for tool in event.data.required_action.submit_tool_outputs.tool_calls:
        if tool.function.name == "distance_search":
            articles: QuerySet = distance_search(
                tool.function.arguments)
            output = []

            for article in articles:
                output.append({"title": article.title, "title_fr": article.title_fr, "content": article.content,
                              "realtive_url": f'/article/?id={article.id}'})

            tool_outputs.append(
                {"tool_call_id": tool.id, "output": json.dumps(output)})

    return tool_outputs
