from datetime import datetime, timezone

from app.services.supabase_client import supabase


def create_table():
    """
    Kept for compatibility with the existing application.

    The chat_history table is already created in Supabase,
    so no local table creation is required.
    """
    pass


def save_chat(chat_id, question, answer):
    """
    Save a chat message to Supabase.
    """

    data = {
        "chat_id": chat_id,
        "question": question,
        "answer": answer,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    response = (
        supabase
        .table("chat_history")
        .insert(data)
        .execute()
    )

    return response.data


def get_chat_history(chat_id):
    """
    Retrieve chat history for a specific chat.
    """

    response = (
        supabase
        .table("chat_history")
        .select("id, chat_id, question, answer, created_at")
        .eq("chat_id", chat_id)
        .order("id")
        .execute()
    )

    history = []

    for row in response.data:
        history.append({
            "id": row["id"],
            "chat_id": row["chat_id"],
            "question": row["question"],
            "answer": row["answer"],
            "created_at": row["created_at"]
        })

    return history