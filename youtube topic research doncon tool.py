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

# List of broader keywords with high-engagement topics
keywords = [
 "Personal finance tips", "Money management", "Financial independence", "Wealth building",  
 "Passive income ideas", "How to save money", "Budgeting strategies", "Smart investing",  
 "Financial planning guide", "How to increase net worth", "How to retire early (FIRE movement)",  
 "Best ways to save money fast", "Emergency fund savings tips", "How to budget for beginners",  
 "50/30/20 budget rule explained", "Frugal living hacks", "Credit score improvement tips",  
 "Best money-saving apps in 2025", "How to get out of debt fast",  
 "Stock market investing for beginners", "Real estate investing strategies",  
 "Best passive income investments", "How to invest in dividend stocks",  
 "Cryptocurrency investment guide", "ETFs vs Mutual Funds: Which is better?",  
 "Best side hustles for extra income", "Online business ideas for beginners",  
 "How to start a freelance business", "High-income skills to learn in 2025",  
 "How to negotiate a salary raise", "Rich vs Poor mindset: Key differences",  
 "Self-discipline habits for financial success", "Best habits of wealthy people",  
 "How to develop a millionaire mindset", "Time management hacks for productivity",  
 "Daily habits of successful entrepreneurs", "Best books for financial literacy",  
 "The psychology of money management", "How to stop impulse spending",  
 "Overcoming procrastination in personal growth", "How to stay motivated for success",  
 "Career growth strategies for young professionals", "Top productivity apps in 2025",  
 "Minimalist money habits for long-term wealth", "Healthy money habits to build in your 20s",  
 "Why budgeting is important for financial success", "Best personal finance courses online",  

 # 🔥 High-Engagement Keywords (Trending Content Topics)
 "Top 5 Money Mistakes You Must Avoid", "Best Passive Income Ideas in 2025",  
 "How to Build Wealth in Your 20s", "How to Save $10,000 in a Year",  
 "Investing for Beginners: Step-by-Step Guide", "The Best Budgeting Hacks No One Talks About",  
 "How to Make Money Online Fast", "Side Hustles That Actually Work in 2025",  
 "How to Pay Off Debt Quickly", "How to Grow a High Net Worth from Scratch",  
 "Top 5 Financial Habits of Millionaires", "Best Investment Strategies for Beginners",  
 "The Secret to Financial Freedom: What No One Tells You",  
 "How to Build Multiple Streams of Income", "How to Increase Your Income Without a Degree",  
 "Why You’re Not Getting Rich and How to Fix It",  
 "Best Online Jobs That Pay Well in 2025", "How to Live Below Your Means Without Feeling Broke",  
 "The Ultimate Guide to Personal Finance for Beginners",  
 "Money-Saving Challenges to Try in 2025", "Best Credit Cards for Beginners",  
 "How to Stop Living Paycheck to Paycheck", "Smart Money Moves to Make in Your 30s"
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
