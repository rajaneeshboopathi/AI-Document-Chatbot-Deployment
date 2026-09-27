from app.services.supabase_client import supabase


def load_registry():
    """
    Kept for compatibility with the existing application.

    The registry is now stored in Supabase,
    so there is no local JSON file to load.
    """
    response = (
        supabase
        .table("documents")
        .select("chat_id, file_hash, filename, storage_path")
        .execute()
    )

    registry = {}

    for row in response.data:
        registry[row["chat_id"]] = {
            "file_hash": row["file_hash"],
            "filename": row["filename"],
            "storage_path": row["storage_path"]
        }

    return registry


def is_file_processed(file_hash, chat_id):
    """
    Check whether the same file is already registered
    for this chat.
    """

    response = (
        supabase
        .table("documents")
        .select("id")
        .eq("chat_id", chat_id)
        .eq("file_hash", file_hash)
        .limit(1)
        .execute()
    )

    return len(response.data) > 0


def get_registered_file(chat_id):
    """
    Get the currently registered document for a chat.
    """

    response = (
        supabase
        .table("documents")
        .select("chat_id, file_hash, filename, storage_path")
        .eq("chat_id", chat_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    row = response.data[0]

    return {
        "file_hash": row["file_hash"],
        "filename": row["filename"],
        "storage_path": row["storage_path"]
    }


def register_file(file_hash, filename, chat_id, storage_path=""):
    """
    Register or replace the current document for a chat.
    """

    data = {
        "chat_id": chat_id,
        "file_hash": file_hash,
        "filename": filename,
        "storage_path": storage_path
    }

    response = (
        supabase
        .table("documents")
        .upsert(
            data,
            on_conflict="chat_id"
        )
        .execute()
    )

    return response.data