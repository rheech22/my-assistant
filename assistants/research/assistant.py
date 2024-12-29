import os
from openai import OpenAI

instructions = """
    You are a research expert.
    Your task is to use Wikipedia or DuckDuckGo to gather comprehensive and accurate information about the query provided. 
    When you find a relevant website through DuckDuckGo, you must scrape the content from that website. Use this scraped content to thoroughly research and formulate a detailed answer to the question. 
    Combine information from Wikipedia, DuckDuckGo searches, and any relevant websites you find. Ensure that the final answer is well-organized and detailed, and include citations with links (URLs) for all sources used.
    Your research should be saved to a .txt file, and the content should match the detailed findings provided. Make sure to include all sources and relevant information.
    The information from Wikipedia must be included.
    Ensure that the final .txt file contains detailed information, all relevant sources, and citations.
"""

# ! when assistant is not created yet, create it and then set the assistant's id as an environment variable
# assistant = client.beta.assistants.create(
#     name="Research Expert",
#     instructions=instructions,
#     model="gpt-4o-mini",
#     tools=functions, # functions from functions.py
# )

# set the assistant's id as an environment variable
assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")


class Assistant:
    def __init__(self, assistant_id, event_handler_factory):
        self.client = OpenAI()
        self.assistant_id = assistant_id
        self.event_handler_factory = event_handler_factory
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id

    def query(self, content, chat_callback):
        event_handler = self.event_handler_factory(
            client=self.client, chat_callback=chat_callback
        )
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            event_handler=event_handler,
            additional_messages=[{"role": "user", "content": content}],
        ) as stream:
            stream.until_done()
        return event_handler.answer

    def get_messages(self, thread_id):
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        messages = list(messages)
        messages.reverse()
        result = []
        for message in messages:
            result.append(f"{message.role}: {message.content[0].text.value}")
        return result


# example usage
# assistant = Assistant(assistant_id, event_handler_factory)
# thread_id = assistant.query("I want to know about the path of exile game.")
# assistant.get_messages(thread_id)
