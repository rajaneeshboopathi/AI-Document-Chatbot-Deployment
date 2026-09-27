from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Form
)

import os
import uuid

from app.services.ingestion import ingest_document

from app.services.file_utils import (
    calculate_file_hash
)

from app.services.document_registry import (
    is_file_processed,
    register_file,
    get_registered_file
)

from app.services.vector_store import (
    delete_chat_documents_except,
    delete_document_by_file_hash
)

from app.services.supabase_storage import (
    upload_document,
    delete_document,
    get_content_type
)

from app.utils.logger import logger


router = APIRouter()


UPLOAD_FOLDER = "data/uploads"


@router.post("/upload")
async def upload_document_route(
    chat_id: str = Form(...),
    file: UploadFile = File(...)
):

    # --------------------------------------------------
    # Validate chat ID
    # --------------------------------------------------

    if not chat_id.strip():

        logger.warning(
            "Upload attempted without a chat ID"
        )

        raise HTTPException(
            status_code=400,
            detail="Chat ID is required"
        )


    # --------------------------------------------------
    # Validate filename
    # --------------------------------------------------

    if not file.filename:

        logger.warning(
            "Upload attempted without a filename"
        )

        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )


    logger.info(
        f"Upload started: "
        f"{file.filename} | "
        f"Chat ID: {chat_id}"
    )


    # --------------------------------------------------
    # Validate extension
    # --------------------------------------------------

    allowed_extensions = [
        ".pdf",
        ".txt",
        ".docx"
    ]

    file_extension = os.path.splitext(
        file.filename
    )[1].lower()


    if file_extension not in allowed_extensions:

        logger.warning(
            f"Unsupported file type: "
            f"{file.filename}"
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF, TXT, and DOCX files "
                "are supported"
            )
        )


    # --------------------------------------------------
    # Secure filename
    # --------------------------------------------------

    safe_filename = os.path.basename(
        file.filename
    )


    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


    # --------------------------------------------------
    # Temporary file
    # --------------------------------------------------

    temporary_filename = (
        f".tmp_"
        f"{uuid.uuid4().hex}"
        f"{file_extension}"
    )


    temporary_path = os.path.join(
        UPLOAD_FOLDER,
        temporary_filename
    )


    # --------------------------------------------------
    # Save temporary file
    # --------------------------------------------------

    try:

        with open(
            temporary_path,
            "wb"
        ) as buffer:

            content = await file.read()

            buffer.write(content)

        logger.info(
            f"Temporary file saved: "
            f"{temporary_filename}"
        )

    except Exception as error:

        logger.exception(
            f"Failed to save temporary file: "
            f"{error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file"
        )


    # --------------------------------------------------
    # Calculate hash
    # --------------------------------------------------

    try:

        file_hash = calculate_file_hash(
            temporary_path
        )

    except Exception as error:

        logger.exception(
            f"Failed to calculate file hash: "
            f"{error}"
        )

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to process file"
        )


    # --------------------------------------------------
    # Duplicate check
    # --------------------------------------------------

    if is_file_processed(
        file_hash,
        chat_id
    ):

        logger.warning(
            f"Duplicate document detected: "
            f"{safe_filename}"
        )

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        return {
            "message": (
                "Document already exists "
                "in this chat. "
                "Processing skipped."
            ),
            "filename": safe_filename,
            "duplicate": True,
            "chat_id": chat_id
        }


    # --------------------------------------------------
    # Get previous document information
    # --------------------------------------------------

    previous_document = get_registered_file(
        chat_id
    )


    # --------------------------------------------------
    # Process NEW document first
    # --------------------------------------------------

    try:

        total_chunks = ingest_document(
            temporary_path,
            chat_id,
            document_name=safe_filename
        )

        logger.info(
            f"New document processed successfully: "
            f"{safe_filename} | "
            f"Chunks: {total_chunks} | "
            f"Chat ID: {chat_id}"
        )

    except Exception as error:

        logger.exception(
            f"Document processing failed: "
            f"{safe_filename} | {error}"
        )

        # Remove only newly-created vectors
        try:

            delete_document_by_file_hash(
                chat_id,
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to rollback new document vectors"
            )

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document processing failed: "
                f"{str(error)}"
            )
        )


    # --------------------------------------------------
    # Upload new document to Supabase Storage
    # --------------------------------------------------

    storage_path = (
        f"{chat_id}/"
        f"{file_hash}"
        f"{file_extension}"
    )


    try:

        upload_document(
            temporary_path,
            storage_path,
            get_content_type(file_extension)
        )

        logger.info(
            f"Document uploaded to Supabase Storage: "
            f"{storage_path}"
        )

    except Exception as error:

        logger.exception(
            f"Failed to upload document to "
            f"Supabase Storage: {error}"
        )

        # Rollback new vectors
        try:

            delete_document_by_file_hash(
                chat_id,
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to rollback vectors "
                "after Storage upload failure"
            )

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to store uploaded document"
            )
        )


    # --------------------------------------------------
    # Remove old document vectors
    # --------------------------------------------------

    try:

        delete_chat_documents_except(
            chat_id,
            file_hash
        )

        logger.info(
            f"Previous document vectors removed "
            f"from chat: {chat_id}"
        )

    except Exception as error:

        logger.exception(
            f"Failed to remove previous "
            f"document vectors: {error}"
        )

        # Rollback new vectors
        try:

            delete_document_by_file_hash(
                chat_id,
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to rollback new vectors"
            )

        # Remove newly uploaded Storage object
        try:

            delete_document(
                storage_path
            )

        except Exception:

            logger.exception(
                "Failed to remove uploaded "
                "Storage object during rollback"
            )

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to replace the "
                "current document"
            )
        )


    # --------------------------------------------------
    # Remove previous document from Storage
    # --------------------------------------------------

    if previous_document:

        previous_storage_path = (
            previous_document.get(
                "storage_path"
            )
        )

        if previous_storage_path:

            try:

                delete_document(
                    previous_storage_path
                )

                logger.info(
                    f"Previous document removed "
                    f"from Storage: "
                    f"{previous_storage_path}"
                )

            except Exception:

                # Do not destroy the new upload
                logger.exception(
                    "Failed to remove previous "
                    "Storage object"
                )


    # --------------------------------------------------
    # Register new document
    # --------------------------------------------------

    try:

        register_file(
            file_hash,
            safe_filename,
            chat_id,
            storage_path
        )

        logger.info(
            f"Document registered successfully: "
            f"{safe_filename} | "
            f"Chat ID: {chat_id}"
        )

    except Exception as error:

        logger.exception(
            f"Failed to register document: "
            f"{error}"
        )

        # Rollback newly-created vectors
        try:

            delete_document_by_file_hash(
                chat_id,
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to rollback vectors "
                "after registry failure"
            )

        # Remove new Storage object
        try:

            delete_document(
                storage_path
            )

        except Exception:

            logger.exception(
                "Failed to remove Storage object "
                "after registry failure"
            )

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processed but "
                "failed to update document registry"
            )
        )


    # --------------------------------------------------
    # Delete temporary local file
    # --------------------------------------------------

    try:

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        logger.info(
            f"Temporary file deleted: "
            f"{temporary_filename}"
        )

    except Exception:

        logger.exception(
            "Failed to delete temporary file"
        )


    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "message": (
            "File uploaded and processed "
            "successfully"
        ),
        "filename": safe_filename,
        "chunks_created": total_chunks,
        "duplicate": False,
        "chat_id": chat_id
    }