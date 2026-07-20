from app.services.youtube_service import search_youtube

videos = search_youtube(
    "Operating System Process Scheduling",
    max_results=5
)

print()

print("=" * 70)

for i, video in enumerate(videos, start=1):

    print(f"\nVideo {i}")

    print("-" * 70)

    print("Title      :", video["title"])
    print("Channel    :", video["channel"])
    print("Published  :", video["published_at"])
    print("URL        :", video["url"])

print("\nTotal Videos :", len(videos))