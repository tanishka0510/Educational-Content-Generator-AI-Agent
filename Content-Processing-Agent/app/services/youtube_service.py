import os

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

YOUTUBE_API_KEY= os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY 
)


def search_youtube(query: str, max_results: int = 5):
    """
    Search educational YouTube videos.
    """

    education_keywords = ["what","how","why","explain","define","algorithm","stack","queue","tree","graph","python","java","c++","database","sql",]

    if any(word in query.lower() for word in education_keywords):
        query = f"{query} tutorial"

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results,
        videoEmbeddable="true",
        videoDuration="medium"
    )

    try:
        response = request.execute()
    except Exception as e:
        print("YouTube API Error:", e)
        return []

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