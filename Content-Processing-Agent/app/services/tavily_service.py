from tavily import TavilyClient

from app.core.config import settings


client = TavilyClient(api_key=settings.TAVILY_API_KEY)


def search_tavily(query: str):
    """
    Search the web using Tavily.

    Returns:
        context -> text to send to Gemini
        sources -> list of URLs
    """

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=settings.TAVILY_MAX_RESULTS,
    )

    context = ""
    sources = []

    for result in response.get("results", [])[:3]:

        context += (
            f"Title: {result['title']}\n"
            f"Content: {result['content']}\n\n"
        )

        sources.append(result["url"])

    return context, sources