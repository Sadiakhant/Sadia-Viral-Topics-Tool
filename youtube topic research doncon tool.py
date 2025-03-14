import streamlit as st
from googleapiclient.discovery import build
import datetime

# YouTube API Configuration
API_KEY = "AIzaSyACH1qjm6FuvEgvgxdA898_dDkMolyYcIM"  # Your API Key
youtube = build("youtube", "v3", developerKey=API_KEY)

# Input Fields
max_results = st.slider("Select Number of Trending Videos", 5, 50, 10)

# Calculate Date for Past 7 Days
seven_days_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat() + "Z"

# Target Keywords for Your Niche
keywords = [
    "Funny travel", "Travel humor", "Country facts", "Weird laws", "Funny geography",
    "Hilarious maps", "Travel jokes", "Comedic travel", "Funny world facts",
    "Strange countries", "Crazy borders", "Quirky culture", "Odd traditions",
    "Hidden gems", "Bizarre places", "Fun geography", "Wacky travel",
    "Travel memes", "Unexpected facts", "Tourist mistakes", "Smallest countries",
    "Funny stereotypes", "Weirdest foods", "Hilarious accents", "Travel fails",
    "Funny comparisons", "Comedic history", "Surprising travel", "Humor travel guide",
    "Odd travel tips", "Unique countries", "Weird world", "Strange landmarks",
    "Obscure places", "Tiny nations", "Wacky history", "Fun world trivia",
    "Shocking facts", "Funny maps", "Comedic facts", "Weird cultures",
    "Ridiculous customs", "Bizarre traditions", "Hilarious history", "Geography humor",
    "Travel comedy", "Funny travel show", "Odd geography", "Crazy travel tips",
    "Satirical travel", "Humorous maps"
]

# Function to Search for Trending Videos in the Niche
def get_trending_videos():
    trending_videos = []
    for keyword in keywords:
        request = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            order="viewCount",
            maxResults=max_results,
            publishedAfter=seven_days_ago  # Fetches videos from the past 7 days
        )
        response = request.execute()
        
        for item in response.get("items", []):
            video_data = {
                "Title": item["snippet"]["title"],
                "Channel": item["snippet"]["channelTitle"],
                "Published Date": item["snippet"]["publishedAt"],
                "Video Link": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            trending_videos.append(video_data)
    
    return trending_videos

# Fetch Trending Videos
if st.button("Find Trending Videos"):
    trending_videos = get_trending_videos()
    
    if trending_videos:
        st.write("### Trending Videos in Your Niche 🎬 (Past 7 Days)")
        for video in trending_videos:
            st.write(f"📌 **{video['Title']}**  \n🎥 Channel: {video['Channel']}  \n🗓 Published: {video['Published Date']}  \n🔗 [Watch Video]({video['Video Link']})")
    else:
        st.write("No trending videos found for your niche right now. Try again later!")
