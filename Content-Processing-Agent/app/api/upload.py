"""
Upload API
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional

from app.models.document import Document
from app.services.storage_service import StorageService

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
async def upload_document(
    subject: Optional[str] = Form(default=None),
    file: UploadFile = File(...)
):
    from app.services.processing_service import ProcessingService
    
    """
    Upload and process a document for the selected subject.
    Subject is optional (defaults to GENERAL) to support Chat document uploads without subject selection.
    """

    # Process subject if provided
    clean_subject = subject.strip() if subject and subject.strip() else None

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
            selected_subject=clean_subject,
        )

    except HTTPException:
        raise

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print("Document processing error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Could not process the uploaded document: {str(e)}"
        )

    # =====================================================
    # Return Success
    # =====================================================

    return {
        "message": "File uploaded successfully.",
        "filename": document.filename,
        "file_type": document.file_type,
        "subject": document.subject,
        "topic": document.topics[0] if document.topics else None,
        "chunks_created": len(document.chunks),
        "embedding_dimension": (
            len(document.chunks[0].embedding)
            if document.chunks and document.chunks[0].embedding
            else 0
        ),
        "status": "Indexed successfully"
    }