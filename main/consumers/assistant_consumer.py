""" Django-Channels consumer for interacting with an AI assistant. """

import json
from uuid import uuid4

from channels.generic.websocket import WebsocketConsumer
from django.utils.translation import get_language
from django.template.loader import render_to_string

from main.assistant_utils import create_assistant, process_req_action
from openai import OpenAI
from markdown import markdown


class AssistantConsumer(WebsocketConsumer):
    """ Handle websocket connections and communicating with an OpenAI Assistant. """

    client = OpenAI()

    def connect(self) -> None:
        """ Get current language, initialize assistant, create a thread, accept connection and start streaming so that the assistant can introduce itself. """
        lang = get_language()
        assistant, thread = create_assistant(lang)

        self.assistant = assistant
        self.thread = thread

        self.accept()
        self.stream()

    def disconnect(self, close_code) -> None:
        pass

    def receive(self, text_data) -> None:
        """ Send rendered user message, add it to the assistant thread and stream response. """

        text_data_json = json.loads(text_data)
        user_input = text_data_json["user-input"]
        user_msg_id = f"user-{uuid4().hex}"

        msg_tmp = render_to_string(
            "main/assistant/message.html", context={"id": user_msg_id,
                                                    "content": user_input,
                                                    "role": "user",
                                                    "swap_mode": ""})

        self.send(
            text_data=self.wrap_msg(msg_tmp))

        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_input,
        )

        self.stream()

    def stream(self) -> None:
        """ Create a stream run and send messages and deltas. """

        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        ) as stream:
            self.handle_events(stream)

    def handle_events(self, stream) -> None:
        """ Listens for events and reacts accordingly:
                - Returns an empty message on message creation. 
                - Returns deltas (bits of text) to be inserted inside the message.
                - Triggers a function and handles the output on 'required action' event.
                - Formats message content in HTML on message completed, and actualizes the message.
        """

        for event in stream:
            if event.event == "thread.message.created":

                # Il est nécessaire de pouvoir identifier le message pour y insérer les deltas par la suite.
                self.curr_msg_id = f'msg_{uuid4().hex}'

                msg_tmp = render_to_string(
                    "main/assistant/message.html", context={"id": self.curr_msg_id,
                                                            "content": "",
                                                            "role": "assistant",
                                                            "swap_mode": "beforeend"})
                self.send(
                    text_data=self.wrap_msg(msg_tmp))

            if event.event == "thread.message.delta":

                txt = event.data.delta.content[0].text.value

                msg_tmp = render_to_string(
                    "main/assistant/message.html", context={"id": self.curr_msg_id,
                                                            "content": txt,
                                                            "role": "assistant",
                                                            "swap_mode": "beforeend"})

                self.send(text_data=msg_tmp)

            if event.event == 'thread.run.requires_action':
                tool_outputs = process_req_action(event)

                with self.client.beta.threads.runs.submit_tool_outputs_stream(
                    thread_id=self.thread.id,
                    run_id=stream.current_run.id,
                    tool_outputs=tool_outputs,
                ) as stream:
                    self.handle_events(stream)

            if event.event == "thread.message.completed":

                # Plutot que de streamer du HTML, on formate le message à la fin, afin d'éviter que certains deltas ('</' ou '>') passent à la trappe.
                txt = markdown(event.data.content[0].text.value)

                msg_tmp = render_to_string(
                    "main/assistant/message.html", context={"id": self.curr_msg_id,
                                                            "content": txt,
                                                            "role": "assistant",
                                                            "swap_mode": "innerHTML"})
                self.send(text_data=msg_tmp)

    @staticmethod
    def wrap_msg(msg_tmp) -> str:
        """ Wraps a message in a section, so that HTMX can identify the section as the target (out of band swap). """

        return f'<section id="messages" class="messages" hx-swap-oob="beforeend">{msg_tmp}</section>'
