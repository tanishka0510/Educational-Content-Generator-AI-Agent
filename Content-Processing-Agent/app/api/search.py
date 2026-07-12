"""
Search API

Performs semantic search on indexed documents.
"""

from fastapi import APIRouter, HTTPException,Query

from app.services.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.post("/")
async def search_documents(
    query: str = Query(
        ...,
        description="Search query"
    ),
    top_k: int = Query(
        5,
        ge=1,
        description="Number of results to retrieve"
    )
):
    """
    Search indexed documents using semantic similarity.

    Parameters
    ----------
    query : str
        User query.

    top_k : int
        Number of chunks to retrieve.

    Returns
    -------
    dict
        Search results.
    """

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    results = RetrievalService.search(
        query=query,
        top_k=top_k
    )

    formatted_results = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        formatted_results.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": distance
            }
        )

    return {
        "query": query,
        "total_results": len(formatted_results),
        "results": formatted_results
    }