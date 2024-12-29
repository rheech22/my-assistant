import streamlit as st
import os
from assistants.research.assistant import Assistant
from assistants.research.event_handler import event_handler_factory


# chat
def paint_history():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False,
        )


def save_message(message, role):
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
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
    page_title="My Assistant",
    page_icon="🔆",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/rheech22/my-assistant/issues",
        "Report a bug": "https://github.com/rheech22/my-assistant/issues",
        "About": "### This is a my assistant to help me with my daily tasks.",
    },
)

with st.sidebar:
    st.title("My Assistant")
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
    message = st.chat_input("Ask anything about your file...")
    assistant = Assistant(event_handler_factory=event_handler_factory, api_key=api_key)
    if message:
        send_message(message, "human")
        assistant.query(message, chat_callback=chat_callback)
        if is_file_exists():
            st.download_button(
                label="Download output.txt",
                data=read_output_file(),
                file_name="output.txt",
                mime="text/plain",
            )
        with st.sidebar:
            st.write(st.session_state["messages"])
else:
    st.markdown(
        """
    ## Welcome!
                
    ### Use this agent to ask to research about What you want to know.

    - this agent will help you to find the information you need.
    - OPENAI API KEY is required to use this agent.
    - Just type in the message box and press Enter.
    """
    )
    st.session_state["messages"] = []
