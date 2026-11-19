from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.db.database import init_db
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


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


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