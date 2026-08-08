from duckduckgo_search import DDGS


def search_duckduckgo(query: str):
    """
    Search DuckDuckGo.

    Returns
    -------
    context : str
        Text to send to Gemini.

    sources : list[str]
        Source URLs.
    """

    context = ""
    sources = []

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=5,
                )
            )

        for result in results:

            title = result.get("title", "")
            body = result.get("body", "")
            url = result.get("href", "")

            context += (
                f"Title: {title}\n"
                f"Content: {body}\n\n"
            )

            if url:
                sources.append(url)

    except Exception as e:

        print("\nDuckDuckGo Search Error")
        print(e)

    return context, sources