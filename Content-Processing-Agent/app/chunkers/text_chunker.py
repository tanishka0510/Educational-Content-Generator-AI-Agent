"""
Text Chunker

Splits cleaned text into overlapping chunks
for embeddings and retrieval.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """
    Splits text into semantic chunks.
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                "? ",
                "! ",
                " ",
                "",
            ],
        )

    def chunk(self, text: str) -> list[str]:
        """
        Split text into chunks.

        Parameters
        ----------
        text : str

        Returns
        -------
        list[str]
        """

        if not text.strip():
            return []

        return self.splitter.split_text(text)