import requests
import streamlit as st

from api_client import error_detail, post_image

TASKS = {
    "Describe the image": "describe",
    "Identify objects": "objects",
    "Explain a diagram": "diagram",
    "Read text in the image": "read_text",
    "Extract info from a screenshot": "screenshot",
    "Ask a question about the image": "question",
}


def render_image_assistant():
    st.subheader("Image assistant")
    st.caption(
        "Upload a non-private image (JPG, PNG or WEBP, up to 5 MB). The image is sent to Google. "
        "AI can misread images, so check important details."
    )

    uploaded = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png", "webp"], key="image_file"
    )
    if uploaded is None:
        st.info("Upload an image to get started.")
        return
    if len(uploaded.getvalue()) > 5 * 1024 * 1024:
        st.error("This image is larger than 5 MB. Please upload a smaller one.")
        return

    st.image(uploaded.getvalue(), caption=uploaded.name, width=400)

    label = st.selectbox("What do you need?", list(TASKS), key="image_task")
    task = TASKS[label]
    question = ""
    if task == "question":
        question = st.text_input("Your question about the image", key="image_question")

    if st.button("Analyze", key="image_run"):
        if task == "question" and not question.strip():
            st.warning("Please type a question first.")
            return
        with st.spinner("Looking at the image..."):
            try:
                result = post_image(
                    uploaded.name,
                    uploaded.getvalue(),
                    uploaded.type or "image/jpeg",
                    task,
                    question.strip(),
                )
            except requests.RequestException as error:
                st.error(error_detail(error))
                return
        st.markdown(result["result"])