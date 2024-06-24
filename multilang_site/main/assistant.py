import logging
from django.template import Template, loader
from openai import OpenAI
from pgvector.django import CosineDistance
from main.models import Article
client = OpenAI()

assistant = client.beta.assistants.create(
    name="BlogAssistant",
    description="You are an assistant for a blog platform. You can help users write blog posts, you can also perform searches and return existing articles from the database.",
    instructions="Keep answers short and to the point. If your response includes lists, emphasis, bold text or paragraphs use appropriate HTML elements (<ul>,<p>,<em>,<b>). Start every conversation by introducing yourself.",
    tools=[{
        "type": "function",
        "function": {
            "name": "distance_search",
            "description": "Perform a search based on an article description in a vector database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_request": {
                        "type": "string",
                        "description": "The description of the kind of article the user is looking for."
                    },
                },
                "required": ["user_request"]
            }
        }
    },],
    model="gpt-4o",
)


def get_embedding(text: str, model="text-embedding-3-small"):
    """ Generate embedding using OpenAI API. """

    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def distance_search(article_desc: str):
    """ Run a similarity search in database with provided article description. """

    embedding = get_embedding(article_desc, model='text-embedding-3-small')

    matching_articles = Article.objects.annotate(
        distance=CosineDistance("embedding", embedding)
    ).order_by("distance")

    return matching_articles


def stream_to_template(request, template_name: str, thread_id: str):
    """ Create a stream run and yield messages.

    Args:
        thread_id (str): Unique ID of existing OpenAI Assistant thread.
    """

    t: Template = loader.get_template(template_name)

    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant.id,
    ) as stream:
        for event in stream:
            if event.event == "thread.message.completed":
                logging.warn(event.data)
                yield t.render(request=request, context={"role": "assistant", "content": event.data.content[0].text.value})
