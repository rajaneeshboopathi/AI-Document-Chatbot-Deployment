from fastapi import (
    APIRouter,
    HTTPException,
    Query
)

from app.services.chat_history import (
    create_table,
    get_chat_history
)


router = APIRouter()


create_table()


@router.get("/history")
def history(
    chat_id: str = Query(...)
):

    if not chat_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Chat ID is required"
        )

    return {
        "chat_id": chat_id,
        "history": get_chat_history(
            chat_id
        )
    }