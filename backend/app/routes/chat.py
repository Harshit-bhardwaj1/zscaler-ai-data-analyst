from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest
from app.services.agent import analyze_question


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        result = analyze_question(
            question=request.question,
            db=db,
            conversation_history=getattr(request, "conversation_history", None),
        )

        return {
            "success": True,
            **result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )