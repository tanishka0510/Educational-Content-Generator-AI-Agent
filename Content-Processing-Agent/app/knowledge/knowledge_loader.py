from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredMarkdownLoader,
)
from app.services.metadata_service import MetadataService

# ==========================================================
# Load Documents From One Subject Folder
# ==========================================================

def load_documents(subject_folder: Path):

    if not subject_folder.exists():
        raise FileNotFoundError(
            f"Subject folder not found: {subject_folder}"
        )

    print(f"\nLoading Subject : {subject_folder.name}")
    print(f"Folder          : {subject_folder}")

    documents = []

    supported_files = [
        "*.pdf",
        "*.docx",
        "*.pptx",
        "*.txt",
        "*.md",
    ]

    for pattern in supported_files:

        for file in subject_folder.rglob(pattern):

            try:

                print(f"Loading {file.name}")

                suffix = file.suffix.lower()

                if suffix == ".pdf":
                    loader = PyPDFLoader(str(file))

                elif suffix == ".docx":
                    loader = UnstructuredWordDocumentLoader(str(file))

                elif suffix == ".pptx":
                    loader = UnstructuredPowerPointLoader(str(file))

                elif suffix == ".txt":
                    loader = TextLoader(
                        str(file),
                        encoding="utf-8"
                    )

                elif suffix == ".md":
                    loader = UnstructuredMarkdownLoader(str(file))

                else:
                    continue

                loaded_docs = loader.load()

                # ---------- IMPORTANT ----------
                for doc in loaded_docs:
                    page = doc.metadata.get("page", 0)

                    unit = MetadataService.detect_unit(
                      doc.page_content
                    )
                    topic = MetadataService.detect_topic(
                      doc.page_content
                    )
                    doc.metadata = {
                      "subject": subject_folder.name,
                      "source": str(file),
                      "filename": file.name,
                      "page": int(page),
                      "unit": unit,
                      "topic": topic
                    }

                documents.extend(loaded_docs)

            except Exception as e:

                print(f"Skipped {file.name}")
                print(e)

    print(f"\nTotal Documents Loaded : {len(documents)}")

    return documents