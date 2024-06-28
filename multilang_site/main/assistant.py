from typing import Tuple
from django.db.models import QuerySet
from django.utils.html import json
from django.template import Template, loader
from django.utils.log import logging
from openai import OpenAI
from pgvector.django import CosineDistance
from main.models import Article

client = OpenAI()


class AssistantError(Exception):
    def __init__(self):
        super().__init__()


def create_assistant(lang) -> Tuple:
    """ Create an OpenAI assistant and set its id in session for retrieval.

    Args:
        request (HttpRequest): request obj, needed for accessing the section.
    """

    assistant = client.beta.assistants.create(
        name="BlogAssistant",
        description="You are an assistant for a blog platform. \
            You can help users write blog posts, you can also perform searches and return existing articles from the database.",
        instructions=f"Answer in the languague corresponding to this code : {lang} unless asked to switch. \
            Keep answers short and to the point. \
            Format your response in HTML: use appropriate HTML elements (<ul>,<p>,<em>,<b>) but don't wrap the end result in any element. \
            Start every conversation by introducing yourself and explaining what you can do.",
        tools=[{"type": "function",
                "function": {
                    "name": "distance_search",
                    "description": "Perform a search based on an article description in a vector database, \
                    go over the resulting objects and create a list of articles including either the 'title' or 'title_fr' field, \
                    depending on the language the request was made in. \
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
        text (str): text to generate an embedding for.
        model (str): name of OpenAI model to use.
    """

    text = text.replace("\n", " ")

    return client.embeddings.create(input=[text], model=model).data[0].embedding


def distance_search(article_desc: str):
    """ Run a similarity search in database with provided article description.

    Args:
        article_desc (str): user input describing what they want.

    Returns:
        matching_articles (QuerySet): articles that best match the provided description/request.
    """

    embedding = get_embedding(article_desc, model='text-embedding-3-small')

    matching_articles = Article.objects.annotate(
        distance=CosineDistance("embedding", embedding)
    ).order_by("distance")

    return matching_articles


def process_req_action(event):
    """ Trigger search on event, generate tool outputs. """

    tool_outputs = []

    for tool in event.data.required_action.submit_tool_outputs.tool_calls:
        if tool.function.name == "distance_search":
            articles: QuerySet = distance_search(
                tool.function.arguments)
            output = []

            for article in articles:
                output.append({"title": article.title, "title_fr": article.title_fr, "content": article.content,
                              "link": f"<button hx-get='/main/article/?id={article.id}' hx-target='main' hx-push-url='true'>read</button>"})

            tool_outputs.append(
                {"tool_call_id": tool.id, "output": json.dumps(output)})

    return tool_outputs


def stream_to_template(assistant_id, thread_id, template_name: str):
    """ Create a stream run and yield messages.

    Args:
        assistant_id (str)
        thread_id (str)
        template_name (str): path/name of template to use.
        thread_id (str): Unique ID of existing OpenAI Assistant thread.

    Yields:
        rendered template.
    """

    t: Template = loader.get_template(template_name)

    try:
        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
        ) as stream:
            for event in stream:
                if event.event == "thread.message.completed":
                    logging.warning(event.event)
                    yield t.render(context={"role": "assistant",
                                            "content": event.data.content[0].text.value})

                if event.event == 'thread.run.requires_action':
                    tool_outputs = process_req_action(event)

                    with client.beta.threads.runs.submit_tool_outputs_stream(
                        thread_id=thread_id,                       run_id=stream.current_run.id,
                        tool_outputs=tool_outputs,
                    ) as stream:
                        for event in stream:
                            if event.event == "thread.message.completed":
                                yield t.render(context={"role": "assistant",
                                                        "content": event.data.content[0].text.value})

    except Exception as e:
        logging.error(e)
        raise AssistantError(e) from e
