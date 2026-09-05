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

        analysis = DocumentAnalyzer.analyze(cleaned_text, selected_subject=selected_subject)

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

        if selected_subject and selected_subject.strip().upper() not in ("GENERAL", "ALL", ""):

            detected = (document.subject or "").strip().upper()
            expected = selected_subject.strip().upper()

            alias_map = {
                "ARTIFICIAL INTELLIGENCE": "AI",
                "OPERATING SYSTEM": "OS",
                "OBJECT ORIENTED PROGRAMMING": "OOP",
                "DATABASE MANAGEMENT SYSTEM": "DBMS",
                "CRYPTOGRAPHY AND NETWORK SECURITY": "CNS",
                "COMPUTER NETWORKS": "CNS",
                "CN": "CNS",
                "COMPUTER ORGANIZATION AND ARCHITECTURE": "COA",
                "SOFTWARE ENGINEERING": "SE",
                "EFFECTIVE TECHNICAL COMMUNICATION": "ETC",
                "DSA": "DATA STRUCTURE",
            }
            norm_detected = alias_map.get(detected, detected)
            norm_expected = alias_map.get(expected, expected)
            scores = analysis.get("scores", {})

            if norm_detected == norm_expected or scores.get(norm_expected, 0) > 0 or detected in ("GENERAL", "UNKNOWN", ""):
                document.subject = selected_subject
            else:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Uploaded document appears to belong to '{document.subject}', "
                        f"but the selected subject is '{selected_subject}'. "
                        "Please upload a document relevant to the selected subject."
                    ),
                )
        else:
            # Subject is optional (e.g. Chat upload); preserve detected subject or default to GENERAL
            if not document.subject:
                document.subject = analysis.get("subject") or "GENERAL"

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