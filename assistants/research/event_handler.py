from openai import AssistantEventHandler
from typing_extensions import override
from assistants.research.functions import functions_map
import json


class EventHandler(AssistantEventHandler):
    def __init__(self, client, chat_callback=None):
        super().__init__()
        self.client = client
        self.answer = ""
        self.chat_callback = chat_callback

    @override
    def on_message_done(self, message) -> None:
        print(f"on_message_done > message: {message}")
        self.chat_callback(message.content[0].text.value)
        self.answer = message.content[0].text.value

    @override
    def on_end(self):
        run = self.current_run
        print(f"ON_END > run status: {run.status}")
        if run.status != "requires_action":
            return
        required_actions = run.required_action.submit_tool_outputs.tool_calls
        outputs = []
        for action in required_actions:
            action_id = action.id
            function = action.function
            print(
                f"ON_END > calling required action: {function.name} with arg {function.arguments}"
            )
            outputs.append(
                {
                    "output": functions_map[function.name](
                        json.loads(function.arguments)
                    ),
                    "tool_call_id": action_id,
                }
            )
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            run_id=run.id,
            thread_id=run.thread_id,
            tool_outputs=outputs,
            event_handler=EventHandler(
                client=self.client, chat_callback=self.chat_callback
            ),
        ) as stream:
            stream.until_done()


def event_handler_factory(client, chat_callback=None):
    return EventHandler(client=client, chat_callback=chat_callback)
