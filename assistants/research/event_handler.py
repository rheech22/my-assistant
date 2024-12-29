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
    def on_text_created(self, text) -> None:
        print("\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        self.answer += delta.value
        print(delta.value, end="", flush=True)

    @override
    def on_text_done(self, text) -> None:
        print(f"on_text_done > chat_callback: {self.answer}")
        if self.chat_callback:
            print(f"on_text_done > calling chat_callback")
            self.chat_callback(self.answer)

    @override
    def on_end(self):
        run = self.current_run
        print(f"on_tool_call_done > run status: {run.status}")
        if run.status != "requires_action":
            return
        required_actions = run.required_action.submit_tool_outputs.tool_calls
        outputs = []
        for action in required_actions:
            action_id = action.id
            function = action.function
            print(
                f"on_end > calling required action: {function.name} with arg {function.arguments}"
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
