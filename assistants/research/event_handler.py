from openai import AssistantEventHandler
from typing_extensions import override
import assistants.research.functions as functions
import json


class EventHandler(AssistantEventHandler):
    def __init__(self, client):
        super().__init__()
        self.client = client

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
                    "output": functions.functions_map[function.name](
                        json.loads(function.arguments)
                    ),
                    "tool_call_id": action_id,
                }
            )
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            run_id=run.id,
            thread_id=run.thread_id,
            tool_outputs=outputs,
            event_handler=EventHandler(client=self.client),
        ) as stream:
            stream.until_done()


def event_handler_factory(client):
    return EventHandler(client=client)
