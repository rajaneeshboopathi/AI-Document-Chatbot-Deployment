import os

from app.services.supabase_client import supabase


BUCKET_NAME = "documents"


MIME_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
}


def get_content_type(file_extension):
    """
    Return the MIME type for a supported file extension.
    """

    return MIME_TYPES.get(
        file_extension.lower(),
        "application/octet-stream"
    )


def upload_document(
    file_path,
    storage_path,
    content_type
):
    """
    Upload a document to the private Supabase Storage bucket.
    """

    with open(file_path, "rb") as file:

        response = (
            supabase
            .storage
            .from_(BUCKET_NAME)
            .upload(
                path=storage_path,
                file=file,
                file_options={
                    "content-type": content_type,
                    "upsert": "false"
                }
            )
        )

    return response


def delete_document(storage_path):
    """
    Delete a document from Supabase Storage.
    """

    return (
        supabase
        .storage
        .from_(BUCKET_NAME)
        .remove([storage_path])
    )


def download_document(
    storage_path,
    destination_path
):
    """
    Download a private document from Supabase Storage.
    """

    response = (
        supabase
        .storage
        .from_(BUCKET_NAME)
        .download(storage_path)
    )

    with open(destination_path, "wb") as file:
        file.write(response)

    return destination_path