"""
Text Loader

Supports:
- TXT
- Markdown
"""

from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
)


class PlainTextLoader:

    @staticmethod
    def load(file_path: str) -> str:

        if file_path.lower().endswith(".txt"):

            loader = TextLoader(
                file_path,
                encoding="utf-8"
            )

        elif file_path.lower().endswith(".md"):

            loader = UnstructuredMarkdownLoader(file_path)

        else:

            raise ValueError(
                f"Unsupported text file: {file_path}"
            )

        documents = loader.load()

        return "\n".join(
            doc.page_content
            for doc in documents
        )