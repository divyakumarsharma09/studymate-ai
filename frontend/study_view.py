import requests
import streamlit as st

from api_client import error_detail, get_json, post_json


def source_payload(key: str, allow_topic: bool = True):
    options = ["Pasted text", "PDF document"]
    if allow_topic:
        options.insert(0, "Topic")
    choice = st.radio("Source", options, horizontal=True, key=f"{key}_source")

    if choice == "Topic":
        topic = st.text_input("Topic", key=f"{key}_topic").strip()
        return {"topic": topic} if topic else None

    if choice == "Pasted text":
        text = st.text_area("Paste your notes", height=200, key=f"{key}_text").strip()
        return {"text": text} if text else None

    try:
        documents = get_json("/documents")
    except requests.RequestException:
        st.warning("Could not load documents.")
        return None
    if not documents:
        st.info("Upload a PDF on the PDF assistant page first.")
        return None
    names = {
        d["doc_id"]: f"{d['filename']} ({d['chunks']} chunks) - {d['doc_id'][:6]}"
        for d in documents
    }
    doc_id = st.selectbox(
        "Document", list(names), format_func=lambda d: names[d], key=f"{key}_doc"
    )
    return {"doc_id": doc_id}


def call_backend(path: str, payload: dict):
    with st.spinner("Working on it..."):
        try:
            return post_json(path, payload)
        except requests.RequestException as error:
            st.error(error_detail(error))
            return None


def render_summary():
    source = source_payload("sum", allow_topic=False)
    length = st.selectbox("Length", ["short", "medium", "detailed"], index=1, key="sum_length")
    if st.button("Summarize", key="sum_button"):
        if source is None:
            st.warning("Please provide some text or choose a document first.")
            return
        result = call_backend("/summarize", {**source, "length": length})
        if result:
            st.markdown(result["summary"])


STUDY_MODES = {
    "Explain simply": "explain",
    "Revision notes": "notes",
    "Short questions": "short_questions",
    "Long questions": "long_questions",
}


def render_study():
    source = source_payload("study")
    label = st.selectbox("What do you want?", list(STUDY_MODES), key="study_mode")
    if st.button("Generate", key="study_button"):
        if source is None:
            st.warning("Please provide a topic, some text or a document first.")
            return
        result = call_backend("/study", {**source, "mode": STUDY_MODES[label]})
        if result:
            st.markdown(result["result"])


def render_quiz():
    source = source_payload("quiz")
    left, right = st.columns(2)
    count = left.slider("Number of questions", 1, 10, 5, key="quiz_count")
    difficulty = right.selectbox("Difficulty", ["easy", "medium", "hard"], index=1, key="quiz_difficulty")

    if st.button("Generate quiz", key="quiz_button"):
        if source is None:
            st.warning("Please provide a topic, some text or a document first.")
        else:
            result = call_backend("/quiz", {**source, "count": count, "difficulty": difficulty})
            if result:
                for i in range(10):
                    st.session_state.pop(f"quiz_q{i}", None)
                st.session_state.quiz = result["questions"]
                st.session_state.quiz_checked = False

    questions = st.session_state.get("quiz")
    if not questions:
        return

    for i, q in enumerate(questions):
        st.markdown(f"**Q{i + 1}. {q['question']}**")
        st.radio(
            "Choose an answer",
            q["options"],
            index=None,
            key=f"quiz_q{i}",
            label_visibility="collapsed",
        )

    if st.button("Check answers", key="quiz_check"):
        st.session_state.quiz_checked = True

    if st.session_state.get("quiz_checked"):
        score = 0
        for i, q in enumerate(questions):
            correct = q["options"][q["correct_index"]]
            if st.session_state.get(f"quiz_q{i}") == correct:
                score += 1
                st.success(f"Q{i + 1}: correct. {q['explanation']}")
            else:
                st.error(f"Q{i + 1}: the correct answer is: {correct}. {q['explanation']}")
        st.subheader(f"Score: {score} / {len(questions)}")


def render_study_tools():
    st.subheader("Study tools")
    st.caption("AI-made content can contain mistakes. Check it before you rely on it.")
    summary_tab, study_tab, quiz_tab = st.tabs(["Summary", "Study modes", "Quiz"])
    with summary_tab:
        render_summary()
    with study_tab:
        render_study()
    with quiz_tab:
        render_quiz()