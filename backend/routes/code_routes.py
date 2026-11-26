from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.code_assistant import run_code_task

router = APIRouter()

MAX_CODE_CHARS = 20_000


class CodeRequest(BaseModel):
    task: Literal["explain", "find_bugs", "generate", "ask"]
    language: str = Field(default="Python", min_length=1, max_length=30)
    code: Optional[str] = None
    instruction: Optional[str] = Field(default=None, max_length=2000)


@router.post("/code")
def code_endpoint(request: CodeRequest):
    code = request.code.strip() if request.code else ""
    instruction = request.instruction.strip() if request.instruction else ""

    if request.task in ("explain", "find_bugs") and not code:
        raise HTTPException(status_code=400, detail="Please paste some code")
    if request.task in ("generate", "ask") and not instruction:
        raise HTTPException(status_code=400, detail="Please describe what you need")
    if len(code) > MAX_CODE_CHARS:
        raise HTTPException(status_code=413, detail="Code is too long (maximum 20,000 characters)")

    try:
        result = run_code_task(request.task, request.language.strip(), code, instruction)
    except Exception as error:
        print("Code error:", error)
        raise HTTPException(status_code=502, detail="The AI model is not available right now")

    return {"task": request.task, "result": result}
