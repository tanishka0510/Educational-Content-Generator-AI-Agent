"""
Khan Academy Service

Provides educational resources from Khan Academy.

This service does not use an official Khan Academy API because
one is no longer publicly available.

Instead, it generates searchable Khan Academy resource links.
"""

from urllib.parse import quote_plus


BASE_URL = "https://www.khanacademy.org/search?page_search_query="


def search_khan(query: str, max_results: int = 3):
    """
    Return Khan Academy learning resources.

    Parameters
    ----------
    query : str
        User question.

    max_results : int
        Reserved for future implementation.

    Returns
    -------
    list
    """

    search_url = BASE_URL + quote_plus(query)

    return [
        {
            "title": f"Khan Academy Resources for '{query}'",
            "description": (
                "Search Khan Academy articles, videos and exercises "
                "related to this topic."
            ),
            "url": search_url,
            "provider": "Khan Academy"
        }
    ]