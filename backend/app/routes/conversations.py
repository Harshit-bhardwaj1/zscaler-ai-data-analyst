from fastapi import APIRouter


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.get("")
def list_conversations():
    return {
        "success": True,
        "conversations": [],
    }


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    return {
        "success": True,
        "conversation_id": conversation_id,
        "messages": [],
    }