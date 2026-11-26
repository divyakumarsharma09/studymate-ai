import requests
import streamlit as st

from api_client import error_detail, post_json

TASKS = {
    "Explain code line by line": "explain",
    "Find bugs": "find_bugs",
    "Write an example": "generate",
    "Ask a programming question": "ask",
}


def render_code_assistant():
    st.subheader("Code assistant")
    st.caption("AI answers about code can be wrong. Run and test any code before you rely on it.")

    label = st.selectbox("What do you need?", list(TASKS), key="code_task")
    task = TASKS[label]
    language = st.text_input("Programming language", value="Python", key="code_language")

    code = ""
    instruction = ""
    if task in ("explain", "find_bugs"):
        code = st.text_area("Paste your code", height=250, key="code_text")
    else:
        instruction = st.text_area("Describe what you need", height=120, key="code_instruction")

    if st.button("Run", key="code_run"):
        payload = {"task": task, "language": language.strip() or "Python"}
        if code.strip():
            payload["code"] = code
        if instruction.strip():
            payload["instruction"] = instruction
        with st.spinner("Thinking..."):
            try:
                result = post_json("/code", payload)
            except requests.RequestException as error:
                st.error(error_detail(error))
                return
        st.markdown(result["result"])