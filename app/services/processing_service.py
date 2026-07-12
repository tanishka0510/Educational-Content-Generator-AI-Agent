"""
Processing Service

Coordinates the complete document processing pipeline.

Current Pipeline

Document
    │
    ▼
Loader
    │
    ▼
Text Cleaner
    │
    ▼
Return Updated Document

More stages (Metadata, Chunking, Embeddings, Database)
will be added later.
"""

from app.models.document import Document
from app.services.document_loading_service import DocumentLoadingService
from app.preprocessors.text_cleaner import TextCleaner
from app.analyzers.document_analyzer import DocumentAnalyzer
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.chroma_service import ChromaService

class ProcessingService:
    """
    Main document processing service.
    """

    @staticmethod
    def process(document: Document) -> Document:
        """
        Process a document.

        Parameters
        ----------
        document : Document
            Uploaded document.

        Returns
        -------
        Document
            Updated document after processing.
        """

        # --------------------------------------------
        # Step 1 : Extract raw text
        # --------------------------------------------
        raw_text = DocumentLoadingService.load(document.file_path)

        document.raw_text = raw_text

        # --------------------------------------------
        # Step 2 : Clean text
        # --------------------------------------------
        cleaned_text = TextCleaner.clean(raw_text)
        document.cleaned_text = cleaned_text
        
        # --------------------------------------------
        # Step 3 : Analyze Document
        # --------------------------------------------
        
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
        
        # --------------------------------------------
        # Step 4 : Chunking Document
        # --------------------------------------------
        
        document = ChunkingService.process(document)
        
        # --------------------------------------------
        # Step 5 : Generate Embeddings
        # --------------------------------------------

        document = EmbeddingService.process(document)
        
        # --------------------------------------------
        # Step 6 : Store in ChromaDB
        # --------------------------------------------

        document = ChromaService.store(document)
        
        # --------------------------------------------
        # Update status
        # --------------------------------------------
        document.status = "indexed"

        return document