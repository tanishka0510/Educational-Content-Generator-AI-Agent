from googleapiclient.discovery import build
from app.core.config import settings


def search_youtube(query: str, max_results: int = 5):
    if not settings.YOUTUBE_API_KEY:
        return []

    try:
        youtube = build(
            "youtube",
            "v3",
            developerKey=settings.YOUTUBE_API_KEY
        )

        response = youtube.search().list(
            part="snippet",
            q=f"{query} tutorial",
            type="video",
            maxResults=max_results,
            videoEmbeddable="true",
            videoDuration="medium"
        ).execute()

        videos = []

        for item in response.get("items", []):
            snippet = item["snippet"]
            video_id = item["id"]["videoId"]

            videos.append({
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "description": snippet["description"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "published_at": snippet["publishedAt"]
            })

        return videos

    except Exception as e:
        print("YouTube API Error:", e)
        return []