"""
Upload API
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from app.models.document import Document
from app.services.storage_service import StorageService
from app.services.processing_service import ProcessingService


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
    Upload and process a document for the selected subject.
    """

    # =====================================================
    # Validate file exists
    # =====================================================

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a file to upload."
        )

    # =====================================================
    # Save file
    # =====================================================

    try:
        saved_file = await StorageService.save_file(file)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        print("File saving error:", e)

        raise HTTPException(
            status_code=500,
            detail="Could not save the uploaded file."
        )

    # =====================================================
    # Create Document
    # =====================================================

    document = Document(
        filename=saved_file["original_filename"],
        file_path=saved_file["file_path"],
        file_type=saved_file["file_type"],
    )

    # =====================================================
    # Process Document
    # =====================================================

    try:

        document = ProcessingService.process(
            document=document,
            selected_subject=subject,
        )

    except ValueError as e:

        # This is where your subject-validation error
        # should be converted into a user-friendly response.

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print("Document processing error:", e)

        raise HTTPException(
            status_code=500,
            detail="Could not process the uploaded document."
        )

    # =====================================================
    # Return Success
    # =====================================================

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