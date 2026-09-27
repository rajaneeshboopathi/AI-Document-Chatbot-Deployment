import os

from app.services.document_loader import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import generate_embedding
from app.services.vector_store import add_chunk
from app.services.file_utils import calculate_file_hash


def ingest_document(
    file_path,
    chat_id,
    document_name=None
):

    if document_name is None:

        document_name = os.path.basename(
            file_path
        )

    file_hash = calculate_file_hash(
        file_path
    )

    pages = extract_text(
        file_path
    )

    total_chunks = 0

    for page in pages:

        page_number = page["page"]

        text = page["text"]

        chunks = chunk_text(
            text
        )

        for chunk_number, chunk in enumerate(
            chunks
        ):

            embedding = generate_embedding(
                chunk
            )

            chunk_id = (
                f"{chat_id}"
                f"_{file_hash}"
                f"_{document_name}"
                f"_page_{page_number}"
                f"_chunk_{chunk_number}"
            )

            metadata = {
                "document": document_name,
                "page": page_number,
                "file_hash": file_hash,
                "chat_id": chat_id
            }

            add_chunk(
                chunk_id=chunk_id,
                text=chunk,
                embedding=embedding,
                metadata=metadata
            )

            total_chunks += 1

    return total_chunks