from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.services.vision import TASKS, run_image_task

router = APIRouter()

MAX_IMAGE_BYTES = 5 * 1024 * 1024


def detect_mime(data: bytes) -> Optional[str]:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


@router.post("/image")
def image_endpoint(
    file: UploadFile = File(...),
    task: str = Form(...),
    question: str = Form(""),
):
    if task not in TASKS:
        raise HTTPException(status_code=400, detail="Unknown task")

    question = question.strip()
    if task == "question" and not question:
        raise HTTPException(status_code=400, detail="Please type your question about the image")
    if len(question) > 1000:
        raise HTTPException(status_code=400, detail="Question is too long (maximum 1,000 characters)")

    data = file.file.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large (maximum 5 MB)")

    mime_type = detect_mime(data)
    if mime_type is None:
        raise HTTPException(status_code=400, detail="Please upload a JPG, PNG or WEBP image")

    try:
        result = run_image_task(task, data, mime_type, question)
    except Exception as error:
        print("Image error:", error)
        raise HTTPException(status_code=502, detail="The AI model is not available right now")

    return {"task": task, "result": result}