""" Chatbot views declarations """

from django.http import StreamingHttpResponse
from django.utils.translation import get_language
from main.assistant import client, create_assistant, stream_to_template
from django.shortcuts import render


def chat_window(request):
    if not request.session.get("thread_id"):
        lang = get_language()
        assistant, thread = create_assistant(lang)

        request.session["thread_id"] = thread.id
        request.session["assistant_id"] = assistant.id
    return render(request, "main/assistant/assistant.html", context={"thread_id": request.session["thread_id"]})


def get_ids(request):

    a = request.session["assistant_id"]
    t = request.session["thread_id"]

    return (a, t)


def receive_messages(request):
    """ View returning the chat window and initialiazing a thread.

    Returns:
        render (HttpResponse): rendered base layout with 'assistant' view in context.
        StreamingHttpResponse: stream of assistant template renderings, with actualized context.
    """

    a, t = get_ids(request)

    return StreamingHttpResponse(stream_to_template(
        assistant_id=a, thread_id=t, template_name="main/assistant/message.html"))


def send_message(request):
    """ Create message from received user input and run stream.

    Returns:
        StreamingHttpResponse: stream of assistant template renderings, with actualized context.
    """

    input = request.POST.get("user-input")
    a, t = get_ids(request)

    client.beta.threads.messages.create(
        thread_id=t,
        role="user",
        content=input,
    )

    return StreamingHttpResponse(stream_to_template(assistant_id=a, thread_id=t, template_name="main/assistant/message.html"))
