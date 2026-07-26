"""
NPTEL Service

Provides educational resources from NPTEL.

Currently this service generates an NPTEL search URL.
It can later be upgraded to retrieve course metadata
or search an indexed NPTEL knowledge base.
"""

from urllib.parse import quote_plus


BASE_URL = "https://nptel.ac.in/courses?search_query="


def search_nptel(query: str, max_results: int = 3):
    """
    Search NPTEL resources.

    Parameters
    ----------
    query : str
        User's question.

    max_results : int
        Reserved for future implementation.

    Returns
    -------
    list
        List containing NPTEL search resource.
    """

    search_url = BASE_URL + quote_plus(query)

    return [
        {
            "title": f"NPTEL Resources for '{query}'",
            "description": (
                "Search NPTEL courses, lecture videos and study "
                "materials related to this topic."
            ),
            "url": search_url,
            "provider": "NPTEL"
        }
    ]