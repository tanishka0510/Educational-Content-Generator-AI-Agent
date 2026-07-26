"""
Office Document Loader

Supports:
- DOCX
- PPTX
"""

from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
)


class OfficeLoader:

    @staticmethod
    def load(file_path: str) -> str:

        if file_path.lower().endswith(".docx"):

            loader = UnstructuredWordDocumentLoader(file_path)

        elif file_path.lower().endswith(".pptx"):

            loader = UnstructuredPowerPointLoader(file_path)

        else:

            raise ValueError(
                f"Unsupported Office file: {file_path}"
            )

        documents = loader.load()

        return "\n".join(
            doc.page_content
            for doc in documents
        )