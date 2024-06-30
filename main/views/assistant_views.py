""" Chatbot views """

from django.shortcuts import render


def chat_window(request):
    """ Open assistant window. """

    return render(request, "main/assistant/assistant.html")
