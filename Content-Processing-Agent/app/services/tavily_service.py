from tavily import TavilyClient
from app.core.config import settings


def search_tavily(query: str, max_results: int = 5):
    if not settings.TAVILY_API_KEY:
        return []

    try:
        client = TavilyClient(
            api_key=settings.TAVILY_API_KEY
        )

        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results
        )

        return [
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")
            }
            for result in response.get("results", [])
        ]

    except Exception as e:
        print("Tavily API Error:", e)
        return []