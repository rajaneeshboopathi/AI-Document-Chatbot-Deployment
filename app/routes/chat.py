from fastapi import (
    APIRouter,
    HTTPException
)

from pydantic import BaseModel

from app.services.rag import answer_question

from app.services.chat_history import (
    create_table,
    save_chat
)

from app.services.chat_session import (
    create_chat_id
)

from app.services.intent_classifier import (
    classify_intent,
    get_casual_response
)

from app.services.bot_identity import (
    get_identity_response
)

from app.utils.logger import logger


router = APIRouter()


create_table()


class ChatRequest(BaseModel):

    question: str

    chat_id: str


@router.post("/new-chat")
def new_chat():

    chat_id = create_chat_id()

    logger.info(
        f"New chat created: {chat_id}"
    )

    return {
        "chat_id": chat_id
    }


@router.post("/chat")
def chat(
    request: ChatRequest
):

    # ====================================
    # 1. Validate chat ID
    # ====================================

    if not request.chat_id.strip():

        logger.warning(
            "Chat request received "
            "without chat ID"
        )

        raise HTTPException(
            status_code=400,
            detail="Chat ID is required"
        )


    # ====================================
    # 2. Validate question
    # ====================================

    if not request.question.strip():

        logger.warning(
            "Chat request received "
            "with empty question"
        )

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )


    logger.info(
        f"Chat request received: "
        f"{request.question} | "
        f"Chat ID: {request.chat_id}"
    )


    # ====================================
    # 3. Detect intent
    # ====================================

    intent = classify_intent(
        request.question
    )


    logger.info(
        f"Detected intent: {intent} | "
        f"Question: {request.question}"
    )


    # ====================================
    # 4. Casual conversation
    # ====================================

    if intent == "casual":

        answer = get_casual_response(
            request.question
        )

        result = {
            "answer": answer,
            "sources": []
        }


    # ====================================
    # 5. Identity question
    # ====================================

    elif intent == "identity":

        answer = get_identity_response(
            request.question
        )

        result = {
            "answer": answer,
            "sources": []
        }


    # ====================================
    # 6. Document question → RAG
    # ====================================

    else:

        try:

            result = answer_question(
                request.question,
                request.chat_id
            )

        except Exception as error:

            logger.exception(
                "Chat processing failed"
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to generate answer: "
                    f"{str(error)}"
                )
            )


    # ====================================
    # 7. Save chat history
    # ====================================

    try:

        save_chat(
            request.chat_id,
            request.question,
            result["answer"]
        )

        logger.info(
            "Chat response generated "
            "and history saved successfully"
        )

    except Exception as error:

        logger.exception(
            "Failed to save chat history"
        )

        logger.warning(
            "Returning answer even though "
            "history could not be saved"
        )


    # ====================================
    # 8. Return response
    # ====================================

    return result