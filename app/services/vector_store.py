import os
import uuid

from dotenv import load_dotenv

from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# QDRANT CONFIGURATION
# ============================================================

QDRANT_URL = os.getenv("QDRANT_URL")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "documents"

# Gemini embedding dimension
VECTOR_SIZE = 768


# ============================================================
# VALIDATE ENVIRONMENT VARIABLES
# ============================================================

if not QDRANT_URL:

    raise ValueError(
        "QDRANT_URL is missing from .env"
    )


if not QDRANT_API_KEY:

    raise ValueError(
        "QDRANT_API_KEY is missing from .env"
    )


# ============================================================
# QDRANT CLIENT
# ============================================================

client = QdrantClient(

    url=QDRANT_URL,

    api_key=QDRANT_API_KEY,
)


# ============================================================
# CONVERT STRING ID → UUID
# ============================================================

def make_qdrant_id(chunk_id):

    """
    Converts our application chunk ID into
    a deterministic UUID that Qdrant accepts.
    """

    return str(

        uuid.uuid5(

            uuid.NAMESPACE_URL,

            chunk_id
        )
    )


# ============================================================
# CREATE COLLECTION IF IT DOES NOT EXIST
# ============================================================

def ensure_collection():

    collections = client.get_collections()

    existing_names = [

        collection.name

        for collection in collections.collections
    ]

    if COLLECTION_NAME not in existing_names:

        client.create_collection(

            collection_name=COLLECTION_NAME,

            vectors_config=VectorParams(

                size=VECTOR_SIZE,

                distance=Distance.COSINE,
            ),
        )

        print(
            f"Created Qdrant collection: "
            f"{COLLECTION_NAME}"
        )

    else:

        print(
            f"Qdrant collection already exists: "
            f"{COLLECTION_NAME}"
        )


# ============================================================
# CREATE PAYLOAD INDEXES
# ============================================================

def ensure_payload_indexes():

    """
    Creates the chat_id payload index.

    chat_id is an exact identifier, so it is
    stored as a keyword field.
    """

    client.create_payload_index(

        collection_name=COLLECTION_NAME,

        field_name="chat_id",

        field_schema="keyword",
    )

    print(
        "Qdrant payload index ready: chat_id"
    )


# ============================================================
# INITIALIZE QDRANT
# ============================================================

ensure_collection()

ensure_payload_indexes()


# ============================================================
# ADD CHUNK
# ============================================================

def add_chunk(
    chunk_id,
    text,
    embedding,
    metadata,
):

    """
    Stores one document chunk in Qdrant.
    """

    qdrant_id = make_qdrant_id(chunk_id)

    point = PointStruct(

        id=qdrant_id,

        # Gemini already returns a Python list.
        # No .tolist() is required.
        vector=embedding,

        payload={
            "text": text,
            **metadata,
        },
    )

    client.upsert(

        collection_name=COLLECTION_NAME,

        points=[point],
    )


# ============================================================
# SEARCH CHUNKS
# ============================================================

def search_chunks(
    query_embedding,
    chat_id,
    top_k=10,
):

    """
    Searches for the most semantically similar
    chunks belonging to the current chat.
    """

    query_filter = Filter(

        must=[

            FieldCondition(

                key="chat_id",

                match=MatchValue(

                    value=chat_id
                ),
            )
        ]
    )

    # Gemini returns a Python list,
    # so .tolist() is not required.
    results = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_embedding,

        query_filter=query_filter,

        limit=top_k,

        with_payload=True,
    )

    documents = []

    metadatas = []

    for result in results.points:

        payload = result.payload or {}

        # Get chunk text
        documents.append(

            payload.get(
                "text",
                ""
            )
        )

        # Remove text from metadata
        metadata = {

            key: value

            for key, value in payload.items()

            if key != "text"
        }

        metadatas.append(metadata)

    return {

        "documents": [

            documents

        ],

        "metadatas": [

            metadatas

        ],
    }


# ============================================================
# DELETE ALL DOCUMENTS FOR A CHAT
# ============================================================

def delete_chat_documents(chat_id):

    """
    Deletes all document chunks belonging
    to a specific chat.
    """

    query_filter = Filter(

        must=[

            FieldCondition(

                key="chat_id",

                match=MatchValue(

                    value=chat_id
                ),
            )
        ]
    )

    client.delete(

        collection_name=COLLECTION_NAME,

        points_selector=query_filter,
    )


# ============================================================
# DELETE ALL DOCUMENTS EXCEPT ONE FILE
# ============================================================

def delete_chat_documents_except(
    chat_id,
    keep_file_hash,
):

    """
    Deletes all documents in a chat except
    the document having keep_file_hash.
    """

    query_filter = Filter(

        must=[

            FieldCondition(

                key="chat_id",

                match=MatchValue(

                    value=chat_id
                ),
            )
        ]
    )

    records, _ = client.scroll(

        collection_name=COLLECTION_NAME,

        scroll_filter=query_filter,

        with_payload=True,

        limit=10000,
    )

    ids_to_delete = []

    for record in records:

        payload = record.payload or {}

        file_hash = payload.get(
            "file_hash"
        )

        if file_hash != keep_file_hash:

            ids_to_delete.append(
                record.id
            )

    if ids_to_delete:

        client.delete(

            collection_name=COLLECTION_NAME,

            points_selector=ids_to_delete,
        )


# ============================================================
# DELETE ONE DOCUMENT BY FILE HASH
# ============================================================

def delete_document_by_file_hash(
    chat_id,
    file_hash,
):

    """
    Deletes all chunks belonging to
    one specific uploaded document.
    """

    query_filter = Filter(

        must=[

            FieldCondition(

                key="chat_id",

                match=MatchValue(

                    value=chat_id
                ),
            )
        ]
    )

    records, _ = client.scroll(

        collection_name=COLLECTION_NAME,

        scroll_filter=query_filter,

        with_payload=True,

        limit=10000,
    )

    ids_to_delete = []

    for record in records:

        payload = record.payload or {}

        if payload.get(
            "file_hash"
        ) == file_hash:

            ids_to_delete.append(
                record.id
            )

    if ids_to_delete:

        client.delete(

            collection_name=COLLECTION_NAME,

            points_selector=ids_to_delete,
        )


# ============================================================
# RESET ENTIRE COLLECTION
# ============================================================

def reset_collection():

    """
    Completely deletes and recreates
    the Qdrant documents collection.

    WARNING:
    This removes all stored vectors.

    The collection is recreated using
    Gemini's 768-dimensional embeddings.
    """

    global client

    try:

        client.delete_collection(

            collection_name=COLLECTION_NAME
        )

        print(

            f"Deleted Qdrant collection: "
            f"{COLLECTION_NAME}"
        )

    except Exception:

        pass

    client.create_collection(

        collection_name=COLLECTION_NAME,

        vectors_config=VectorParams(

            size=VECTOR_SIZE,

            distance=Distance.COSINE,
        ),
    )

    # Recreate payload index
    ensure_payload_indexes()

    print(

        f"Recreated Qdrant collection: "
        f"{COLLECTION_NAME}"
    )