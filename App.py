import streamlit as st
from assistants.research.assistant import Assistant, assistant_id
from assistants.research.event_handler import event_handler_factory

# assistant
assistant = Assistant(
    assistant_id=assistant_id, event_handler_factory=event_handler_factory
)


# chat
def save_message(message, role):
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    st.session_state["messages"].append({"message": message, "role": role})


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)


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


message = st.chat_input("Ask anything about your file...")
send_message("I'm ready! Ask away!", "ai", save=False)

if message:
    send_message(message, "human")
    thread_id = assistant.query(message)
    if thread_id:
        with st.chat_message("ai"):
            response = assistant.get_messages(thread_id)
