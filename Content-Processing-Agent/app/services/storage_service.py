"""
Storage Service

Responsible for:
- Validating uploaded files
- Saving files
- Generating unique filenames
"""

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings


class StorageService:

    @staticmethod
    async def save_file(file: UploadFile) -> dict:
        """
        Save an uploaded file and return file information.
        """

        # ---------------------------------------------
        # Validate filename
        # ---------------------------------------------
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is missing."
            )

        extension = Path(file.filename).suffix.lower()

        allowed_extensions = (
            settings.SUPPORTED_DOCUMENT_TYPES
            + settings.SUPPORTED_IMAGE_TYPES
            + settings.SUPPORTED_AUDIO_TYPES
        )

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {extension}"
            )

        # ---------------------------------------------
        # Read file
        # ---------------------------------------------
        file_bytes = await file.read()

        file_size_mb = len(file_bytes) / (1024 * 1024)

        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"File size exceeds "
                    f"{settings.MAX_UPLOAD_SIZE_MB} MB."
                ),
            )

        # ---------------------------------------------
        # Generate unique filename  
        # ---------------------------------------------
        # UUID is 1a2b3c4d-6e7f-8g9h.pdf 
        # Why rename ?   If two users upload: notes.pdf , then the second upload overwrites the first. UUIDs avoids this problem completely.
        unique_filename = f"{uuid4()}{extension}"

        save_path = (
            Path(settings.UPLOAD_DIR) /
            unique_filename
        )

        # ---------------------------------------------
        # Save file
        # ---------------------------------------------
        with open(save_path, "wb") as buffer:
            buffer.write(file_bytes)

        # ---------------------------------------------
        # Return information
        # ---------------------------------------------
        return {
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": str(save_path),
            "file_type": extension,
            "file_size_mb": round(file_size_mb, 2),
        }