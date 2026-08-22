"""
Processing Service

Coordinates the complete document processing pipeline.

Pipeline

Upload
    ↓
Extract Text
    ↓
Clean Text
    ↓
Analyze Document
    ↓
Validate Subject
    ↓
Chunk
    ↓
Embedding
    ↓
Store in Chroma
"""

from fastapi import HTTPException

from app.models.document import Document
from app.services.document_loading_service import DocumentLoadingService
from app.preprocessors.text_cleaner import TextCleaner
from app.analyzers.document_analyzer import DocumentAnalyzer
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.chroma_service import ChromaService


class ProcessingService:
    """
    Main document processing pipeline.
    """

    @staticmethod
    def process(
        document: Document,
        selected_subject: str | None = None,
    ) -> Document:

        # --------------------------------------------------
        # Step 1 : Extract Raw Text
        # --------------------------------------------------

        raw_text = DocumentLoadingService.load(document.file_path)
        document.raw_text = raw_text

        # --------------------------------------------------
        # Step 2 : Clean Text
        # --------------------------------------------------

        cleaned_text = TextCleaner.clean(raw_text)
        document.cleaned_text = cleaned_text

        # --------------------------------------------------
        # Step 3 : Analyze Document
        # --------------------------------------------------

        analysis = DocumentAnalyzer.analyze(cleaned_text)

        document.subject = analysis["subject"]
        document.topics = analysis["topics"]
        document.keywords = analysis["keywords"]
        document.language = analysis["language"]

        document.metadata = {
            "word_count": analysis["word_count"],
            "character_count": analysis["character_count"],
            "reading_time": analysis["reading_time"],
        }

        # --------------------------------------------------
        # Step 4 : Validate Subject
        # --------------------------------------------------

        if selected_subject:

            detected = (document.subject or "").strip().lower()
            expected = selected_subject.strip().lower()

            if detected != expected:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Uploaded document belongs to '{document.subject}', "
                        f"but the selected subject is '{selected_subject}'. "
                        "Please upload a document relevant to the selected subject."
                    ),
                )

        # --------------------------------------------------
        # Step 5 : Chunking
        # --------------------------------------------------

        document = ChunkingService.process(document)

        # --------------------------------------------------
        # Step 6 : Generate Embeddings
        # --------------------------------------------------

        document = EmbeddingService.process(document)

        # --------------------------------------------------
        # Step 7 : Store in ChromaDB
        # --------------------------------------------------

        document = ChromaService.store(document)

        # --------------------------------------------------
        # Step 8 : Update Status
        # --------------------------------------------------

        document.status = "indexed"

        return document