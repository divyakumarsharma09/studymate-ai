import requests
import streamlit as st

from api_client import get_json, post_json


def start_new_chat():
    st.session_state.conversation_id = None
    st.session_state.messages = []


def load_conversation(conversation_id: int):
    try:
        st.session_state.messages = get_json(f"/conversations/{conversation_id}")
        st.session_state.conversation_id = conversation_id
    except requests.RequestException:
        st.session_state.load_error = True


def render_conversation_list():
    st.sidebar.header("Conversations")
    st.sidebar.button("New chat", on_click=start_new_chat)
    try:
        conversations = get_json("/conversations")
    except requests.RequestException:
        st.sidebar.warning("Could not load conversations.")
        return
    for conv in conversations[:15]:
        label = (conv["title"] or f"Chat {conv['id']}")[:30]
        st.sidebar.button(
            label,
            key=f"conv_{conv['id']}",
            on_click=load_conversation,
            args=(conv["id"],),
        )


def render_chat():
    if "conversation_id" not in st.session_state:
        start_new_chat()

    render_conversation_list()

    if st.session_state.pop("load_error", False):
        st.warning("Could not open that conversation.")

    st.subheader("Chat")
    for message in st.session_state.messages:
        role = "assistant" if message["role"] == "model" else "user"
        with st.chat_message(role):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask anything about your studies")
    if not prompt:
        return

    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {"message": prompt, "conversation_id": st.session_state.conversation_id}
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = post_json("/chat", payload)
            except requests.RequestException:
                st.error("The assistant could not answer right now. Please try again.")
                return
        st.markdown(result["reply"])

    st.session_state.conversation_id = result["conversation_id"]
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "model", "content": result["reply"]})
    st.rerun()