""" Chatbot views declarations """

from django.shortcuts import render


def chat_window(request):
    """ Open assistant windows. """

    return render(request, "main/assistant/assistant.html")
