from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredMarkdownLoader,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_PATH = BASE_DIR / "knowledge_base"
print(KNOWLEDGE_PATH)
print(KNOWLEDGE_PATH.exists())

def load_documents():

    documents = []

    supported_files = [
        "*.pdf",
        "*.docx",
        "*.pptx",
        "*.txt",
        "*.md",
    ]

    for pattern in supported_files:

        for file in KNOWLEDGE_PATH.rglob(pattern):

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
                    loader = TextLoader(str(file), encoding="utf-8")

                elif suffix == ".md":
                    loader = UnstructuredMarkdownLoader(str(file))

                else:
                    continue

                documents.extend(loader.load())

            except Exception as e:

                print(f"Skipped {file.name}")
                print(e)

    print(f"\nTotal Documents Loaded : {len(documents)}")

    return documents