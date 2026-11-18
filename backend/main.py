from fastapi import FastAPI 
from pydantic import BaseModel
from backend.services.llm_client import ask_llm
app=FastAPI()
class ChatRequest(BaseModel):
    message:str
@app.get("/")
def home():
    return{"message":"Studymate AI is running"}
@app.post("/chat")
def chat (request:ChatRequest):
    reply=ask_llm(request.message)
    return{"reply":reply}
