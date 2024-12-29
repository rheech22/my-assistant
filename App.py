import streamlit as st
from assistants.research.assistant import Assistant, assistant_id
from assistants.research.event_handler import event_handler_factory

# assistant
assistant = Assistant(
    assistant_id=assistant_id, event_handler_factory=event_handler_factory
)


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
    save_message(answer, "ai")


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

st.sidebar.title("My Assistant")

send_message("I'm ready! Ask away!", "ai", save=False)
paint_history()
message = st.chat_input("Ask anything about your file...")

if message:
    send_message(message, "human")
    response = assistant.query(message, chat_callback=chat_callback)
    send_message(response, "ai")
    with st.sidebar:
        st.write(st.session_state["messages"])
