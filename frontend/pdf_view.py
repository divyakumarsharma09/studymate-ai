import requests
import streamlit as st

from api_client import error_detail, get_json, post_json, upload_pdf


def render_pdf_assistant():
    st.subheader("PDF assistant")
    st.caption("Upload a non-private PDF with selectable text. Its text is sent to Google to answer your questions.")

    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded is not None and st.button("Process PDF"):
        with st.spinner("Reading and indexing the PDF..."):
            try:
                result = upload_pdf(uploaded.name, uploaded.getvalue())
            except requests.RequestException as error:
                st.error(error_detail(error))
            else:
                st.session_state.selected_doc = result["doc_id"]
                st.success(
                    f"Ready: {result['filename']} "
                    f"({result['pages']} pages, {result['chunks']} chunks)"
                )

    try:
        documents = get_json("/documents")
    except requests.RequestException:
        st.warning("Could not load documents.")
        return
    if not documents:
        st.info("Upload a PDF to get started.")
        return

    names = {
        doc["doc_id"]: f"{doc['filename']} ({doc['chunks']} chunks) - {doc['doc_id'][:6]}"
        for doc in documents
    }
    doc_ids = list(names)
    if st.session_state.get("selected_doc") not in doc_ids:
        st.session_state.selected_doc = doc_ids[-1]

    doc_id = st.selectbox(
        "Choose a document",
        doc_ids,
        format_func=lambda d: names[d],
        key="selected_doc",
    )

    question = st.text_input("Ask a question about this document")
    if st.button("Ask") and question.strip():
        with st.spinner("Searching the document..."):
            try:
                result = post_json(
                    "/ask-pdf", {"doc_id": doc_id, "question": question.strip()}
                )
            except requests.RequestException as error:
                st.error(error_detail(error))
                return
        st.markdown(result["answer"])
        st.caption("Pages looked at: " + ", ".join(str(p) for p in result["sources"]))