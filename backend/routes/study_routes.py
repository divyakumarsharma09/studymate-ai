from typing import Literal, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.rag.vector_store import get_document_text
from backend.services.quiz import generate_quiz
from backend.services.study import MAX_CHARS, study_from_material, study_from_topic

router = APIRouter()


class StudyRequest(BaseModel):
    mode: Literal["explain", "notes", "short_questions", "long_questions"]
    topic: Optional[str] = None
    text: Optional[str] = None
    doc_id: Optional[str] = None


class QuizRequest(BaseModel):
    topic: Optional[str] = None
    text: Optional[str] = None
    doc_id: Optional[str] = None
    count: int = Field(default=5, ge=1, le=10)
    difficulty: Literal["easy", "medium", "hard"] = "medium"


def load_source(topic: Optional[str], text: Optional[str], doc_id: Optional[str]) -> Tuple[str, str]:
    given = [v for v in (topic, text, doc_id) if v is not None]
    if len(given) != 1:
        raise HTTPException(status_code=400, detail="Send exactly one of topic, text or doc_id")

    if topic is not None:
        topic = topic.strip()
        if not topic or len(topic) > 500:
            raise HTTPException(status_code=400, detail="Topic must be 1 to 500 characters")
        return "topic", topic

    if doc_id is not None:
        material = get_document_text(doc_id)
        if not material:
            raise HTTPException(status_code=404, detail="Document not found")
    else:
        material = text.strip()
        if not material:
            raise HTTPException(status_code=400, detail="Text is empty")

    if len(material) > MAX_CHARS:
        raise HTTPException(status_code=413, detail="Text is too long for one request")
    return "study material", material


@router.post("/study")
def study_endpoint(request: StudyRequest):
    kind, content = load_source(request.topic, request.text, request.doc_id)
    try:
        if kind == "topic":
            result = study_from_topic(content, request.mode)
        else:
            result = study_from_material(content, request.mode)
    except Exception as error:
        print("Study error:", error)
        raise HTTPException(status_code=502, detail="The AI model is not available right now")
    return {"mode": request.mode, "result": result}


@router.post("/quiz")
def quiz_endpoint(request: QuizRequest):
    kind, content = load_source(request.topic, request.text, request.doc_id)
    try:
        quiz = generate_quiz(kind, content, request.count, request.difficulty)
    except Exception as error:
        print("Quiz error:", error)
        raise HTTPException(status_code=502, detail="Could not generate a quiz right now")
    return quiz.model_dump()