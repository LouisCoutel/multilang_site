""" Chatbot views declarations """

from django.http import StreamingHttpResponse
from main.assistant import client, create_assistant, stream_to_template
from django.shortcuts import render


def chat_window(request):
    create_assistant(request)
    thread = client.beta.threads.create()
    return render(request, "main/chatbot/chatbot.html", context={"thread_id": thread.id})


def receive_messages(request):
    """ View returning the chat window and initialiazing a thread.

    Returns:
        render (HttpResponse): rendered base layout with 'chatbot' view in context.
        StreamingHttpResponse: stream of chatbot template renderings, with actualized context.
    """
    thread_id = request.GET.get("thread_id")

    return StreamingHttpResponse(stream_to_template(
        request=request, template_name="main/chatbot/message.html", thread_id=thread_id))


def send_message(request):
    """ Create message from received user input and run stream.

    Returns:
        StreamingHttpResponse: stream of chatbot template renderings, with actualized context.
    """

    input = request.POST.get("user-input")

    thread_id = request.POST.get("thread_id")

    client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=input,
    )

    return render(request, template_name="main/chatbot/message.html", context={"role": "user", "content": input})
