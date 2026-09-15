from pydantic import BaseModel, Field
from typing import Any, Optional


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_history: Optional[list[dict[str, Any]]] = None