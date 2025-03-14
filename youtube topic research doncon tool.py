import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key (Updated)
API_KEY = "AIzaSyACH1qjm6FuvEgvgxdA898_dDkMolyYcIM"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-90):", min_value=1, max_value=90, value=5)

# List of broader keywords with high-engagement topics
keywords = [
    "Personal finance tips", "Money management", "Financial independence", "Wealth building",
    "Passive income ideas", "How to save money", "Budgeting strategies", "Smart investing",
    "Financial planning guide", "How to increase net worth", "How to retire early (FIRE movement)",
    "Best ways to save money fast", "Emergency fund savings tips", "How to budget for beginners",
    "Best investment strategies", "How to stop impulse spending", "How to make money online fast",
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range for video searches
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        min_channel_age = datetime.utcnow() - timedelta(days=180)  # Channels must be at least 6 months old
        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"🔎 Searching for keyword: {keyword}")

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 100,  # Fetch 100 videos per keyword
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                st.warning(f"⚠ No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"⚠ Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics,contentDetails", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"⚠ Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Fetch channel statistics (to check subscriber count & creation date)
            channel_params = {"part": "statistics,snippet", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"⚠ Failed to fetch channel statistics for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = {channel["id"]: channel for channel in channel_data["items"]}  # Store channels by ID

            # Collect results
            for video, stat in zip(videos, stats):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                duration = stat["contentDetails"].get("duration", "PT0M")  # ISO 8601 format

                # Convert ISO 8601 duration (e.g., PT2M30S → 2 min 30 sec)
                minutes = sum(
                    int(x[:-1]) * (60 if x.endswith("M") else 1) for x in duration[2:].split("S")[0].split("M") if x
                )

                # Get channel details
                channel_id = video["snippet"]["channelId"]
                channel = channels.get(channel_id, {})
                subs = int(channel.get("statistics", {}).get("subscriberCount", 0))
                created_at = channel.get("snippet", {}).get("publishedAt", "2000-01-01T00:00:00Z")

                # Convert channel creation date
                channel_created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

                # Apply filters:
                if (
                    10000 <= views <= 10000000  # Views must be between 10K and 10M
                    and 0 <= subs <= 10000  # Subscribers must be between 0 and 10K
                    and minutes >= 2  # Video duration must be at least 2 minutes
                    and channel_created < min_channel_age  # Channel must be at least 6 months old
                ):
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                        "Duration (mins)": minutes,
                    })

        # Display results
        if all_results:
            st.success(f"✅ Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"🎬 **Title:** {result['Title']}  \n"
                    f"📜 **Description:** {result['Description']}  \n"
                    f"🔗 **URL:** [Watch Video]({result['URL']})  \n"
                    f"👁 **Views:** {result['Views']}  \n"
                    f"📊 **Subscribers:** {result['Subscribers']}  \n"
                    f"⏳ **Duration:** {result['Duration (mins)']} minutes"
                )
                st.write("---")
        else:
            st.warning("⚠ No results found matching all filters.")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
