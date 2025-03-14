import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyACH1qjm6FuvEgvgxdA898_dDkMolyYcIM"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of broader keywords
keywords = [
 "Houseplant care", "Indoor plant care", "Best indoor plants", "Low-maintenance houseplants",  
 "Watering indoor plants", "How to grow houseplants", "Houseplant fertilizing guide",  
 "Common houseplant mistakes", "Best soil for houseplants", "Best pots for indoor plants",  
 "How to prune indoor plants", "Repotting houseplants", "When to repot indoor plants",  
 "Fast-growing indoor plants", "How to propagate houseplants", "Best plants for small spaces",  
 "Low-light indoor plants", "Best plants for bright light", "Indoor plant lighting guide",  
 "How to create a light map for plants", "Best plants for north-facing windows",  
 "Sheer curtains for plant protection", "How to protect plants from cold drafts",  
 "How to make a plant grow faster", "DIY plant trellis for climbing plants",  
 "How to keep plants upright", "Root-bound plant solutions",  
 "How to prevent overwatering in houseplants", "How to clean plant leaves",  
 "Self-watering planters DIY", "Houseplant humidity hacks",  
 "LECA vs Soil: Which is better?", "How to grow large indoor plants",  
 "Moss pole for climbing plants", "Top 5 houseplant mistakes to avoid",  
 "Why your houseplant is dying and how to fix it", "Best plants for pet owners",  
 "Best plants for beginners", "How to transition plants from soil to water",  
 "Top 10 houseplants for beginners", "Best plants for semi-hydroponics",  
 "Hydroponic houseplants", "Best trailing plants for indoor spaces",  
 "Plants that purify indoor air", "How to keep plants alive indoors",  
 "Common mistakes when growing indoor plants", "Indoor plant care for beginners"
]




# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"Failed to fetch channel statistics for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Collect results
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                if subs < 3000:  # Only include channels with fewer than 3,000 subscribers
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("No results found for channels with fewer than 3,000 subscribers.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
