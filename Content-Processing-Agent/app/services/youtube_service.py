import os

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


def search_youtube(query: str, max_results: int = 5):
    """
    Search educational YouTube videos.
    """

    query = f"{query} tutorial"

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results,
        videoEmbeddable="true",
        videoDuration="medium"
    )

    response = request.execute()

    videos = []

    for item in response.get("items", []):

        video_id = item["id"]["videoId"]

        snippet = item["snippet"]

        videos.append(
            {
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "description": snippet["description"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "published_at": snippet["publishedAt"],
            }
        )

    return videos