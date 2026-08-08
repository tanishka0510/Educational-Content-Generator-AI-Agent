"""
Upload API
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi import Form
from app.models.document import Document
from app.services.storage_service import StorageService
from app.services.processing_service import ProcessingService
import inspect
from app.services.processing_service import ProcessingService

print(inspect.signature(ProcessingService.process))
router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
async def upload_document(
    subject: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a document.
    """

    # Save file
    saved_file = await StorageService.save_file(file)

    # Create document
    document = Document(
        filename=saved_file["original_filename"],
        file_path=saved_file["file_path"],
        file_type=saved_file["file_type"],
    )

    # Process document
    try:

        document = ProcessingService.process(
            document=document,
            selected_subject=subject,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {
        "message": "File uploaded successfully.",
        "filename": document.filename,
        "file_type": document.file_type,
        "chunks_created": len(document.chunks),
        "embedding_dimension": (
            len(document.chunks[0].embedding)
            if document.chunks and document.chunks[0].embedding
            else 0
        ),
        "status": "Indexed successfully"
    }