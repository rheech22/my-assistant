from openai import AssistantEventHandler
from typing_extensions import override
from assistants.research.functions import functions_map
import json


class EventHandler(AssistantEventHandler):
    def __init__(self, client, chat_callback=None, progress_callback=None):
        super().__init__()
        self.client = client
        self.answer = ""
        self.chat_callback = chat_callback
        self.progress_callback = progress_callback

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
            action = action.function
            mapped_function = functions_map[action.name]
            print(
                f"ON_END > calling required action: {action.name} with arg {action.arguments}"
            )
            if self.progress_callback:
                self.progress_callback(mapped_function["description"])
            outputs.append(
                {
                    "output": mapped_function["function"](json.loads(action.arguments)),
                    "tool_call_id": action_id,
                }
            )
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            run_id=run.id,
            thread_id=run.thread_id,
            tool_outputs=outputs,
            event_handler=EventHandler(
                client=self.client,
                chat_callback=self.chat_callback,
                progress_callback=self.progress_callback,
            ),
        ) as stream:
            stream.until_done()


def event_handler_factory(client, chat_callback=None, progress_callback=None):
    return EventHandler(
        client=client, chat_callback=chat_callback, progress_callback=progress_callback
    )
