import requests
import streamlit as st

from api_client import get_json
from chat_view import render_chat
from code_view import render_code_assistant
from image_view import render_image_assistant
from pdf_view import render_pdf_assistant
from study_view import render_study_tools

st.set_page_config(page_title="StudyMate AI", layout="wide")

st.title("StudyMate AI")
st.caption("Your AI study assistant: chat, PDF questions, summaries and quizzes")

try:
    get_json("/")
except requests.RequestException:
    st.error("Cannot reach the backend. Start it with: uvicorn backend.main:app --reload")
    st.stop()

page = st.sidebar.radio(
    "Go to",
    ["Chat", "PDF assistant", "Study tools", "Code assistant", "Image assistant"],
)

if page == "Chat":
    render_chat()
elif page == "PDF assistant":
    render_pdf_assistant()
elif page == "Study tools":
    render_study_tools()
elif page == "Code assistant":
    render_code_assistant()
else:
    render_image_assistant()