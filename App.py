import streamlit as st
import time
import os

from assistants.research.assistant import Assistant
from assistants.research.event_handler import event_handler_factory
from assistants.research.functions import functions_map

# session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# chat
def paint_history():
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False,
        )


def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)


def chat_callback(answer):
    send_message(answer, "ai")


# output file
FILE_PATH = "output/output.txt"


def is_file_exists():
    return os.path.exists(FILE_PATH)


def delete_output_file():
    os.remove(FILE_PATH)


def read_output_file():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        file_data = f.read()
    return file_data


# view
st.set_page_config(
    page_title="My Research Assistant",
    page_icon="🔆",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/rheech22/my-assistant/issues",
        "Report a bug": "https://github.com/rheech22/my-assistant/issues",
        "About": "### This is a my assistant to help me with my daily tasks.",
    },
)


class ProgressBar:
    def __init__(self):
        self._progress = int(0)

    def start(self, text):
        self._bar = st.progress(0, text=text)
        return self._bar

    def progress(self, status):
        self._progress += 10
        if self._progress > 100:
            self._progress = 100
        self._bar.progress(self._progress, text=status)

    def clear(self):
        self._bar.progress(100, "Done !")
        time.sleep(0.3)
        self._bar.empty()


with st.sidebar:
    st.title("My Research Assistant")
    api_key = st.text_input(
        "Write down your OpenAI's API Key",
        placeholder="sh-1234123412341234",
    )
    st.title("Log")

if api_key:
    send_message("I'm ready! Ask away!", "ai", save=False)
    if is_file_exists():
        delete_output_file()
    paint_history()
    progress = ProgressBar()
    message = st.chat_input("Ask anything what you want to know")
    assistant = Assistant(
        event_handler_factory=event_handler_factory,
        api_key=api_key,
        chat_callback=chat_callback,
        progress_callback=progress.progress,
    )
    if message:
        send_message(message, "human")
        progress.start("Thinking to answer...")
        assistant.query(message)
        progress.clear()
        if is_file_exists():
            st.download_button(
                label="Download this response as a file",
                data=read_output_file(),
                file_name="response.txt",
                mime="text/plain",
            )
        with st.sidebar:
            st.write(st.session_state["messages"])

else:
    st.markdown(
        """
    ## Welcome!
                
    ### I Can help you to research information.

    - I will help you to find the information you need.
    - OPENAI API KEY is required to use this agent.
    """
    )
    st.session_state["messages"] = []
