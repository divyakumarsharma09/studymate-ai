import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.db.database import init_db
from backend.rag.chunker import chunk_pages
from backend.rag.pdf_reader import extract_pages
from backend.rag.qa import answer_question
from backend.rag.vector_store import add_document
from backend.services.llm_client import ask_llm
from backend.services.memory import (
    create_conversation,
    save_message,
    get_messages,
    list_conversations,
    conversation_exists,
)

init_db()

app = FastAPI()

UPLOAD_DIR = Path("data/uploads")
MAX_PDF_BYTES = 20 * 1024 * 1024


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class AskPdfRequest(BaseModel):
    doc_id: str
    question: str


@app.get("/")
def home():
    return {"message": "Studymate AI is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    if request.conversation_id is None:
        conversation_id = create_conversation(request.message[:50])
    else:
        if not conversation_exists(request.conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_id = request.conversation_id

    save_message(conversation_id, "user", request.message)
    history = get_messages(conversation_id)

    try:
        reply = ask_llm(history)
    except Exception as error:
        print("LLM error:", error)
        raise HTTPException(status_code=502, detail="The AI model is not available right now")

    save_message(conversation_id, "model", reply)
    return {"conversation_id": conversation_id, "reply": reply}


@app.get("/conversations")
def conversations():
    return list_conversations()


@app.get("/conversations/{conversation_id}")
def conversation_messages(conversation_id: int):
    if not conversation_exists(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return get_messages(conversation_id)


@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    content = file.file.read()
    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF is too large (maximum 20 MB)")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.pdf"
    saved_path.write_bytes(content)

    try:
        pages = extract_pages(str(saved_path))
    except Exception as error:
        print("PDF error:", error)
        raise HTTPException(status_code=400, detail="Could not read this PDF")

    if not pages:
        raise HTTPException(status_code=400, detail="No text found. The PDF may be scanned")

    chunks = chunk_pages(pages)

    try:
        doc_id = add_document(file.filename, chunks)
    except Exception as error:
        print("Embedding error:", error)
        raise HTTPException(status_code=502, detail="Could not process the document right now")

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
    }


@app.post("/ask-pdf")
def ask_pdf(request: AskPdfRequest):
    try:
        result = answer_question(request.question, request.doc_id)
    except Exception as error:
        print("Ask-PDF error:", error)
        raise HTTPException(status_code=502, detail="The AI model is not available right now")

    if result is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return result