"""
TikTok User Data Scraper

Description:
    This script collects TikTok user metadata and all video metadata for a given username using the TikTokApi.

Why:
    To gather structured data (user profile info and videos) from TikTok environmental influencers for downstream persona analysis.

How:
    - Establishes a session using a manually set ms_token (exported as an environment variable).
    - Fetches user metadata (e.g., bio, follower count, total likes).
    - Fetches metadata for all videos posted by the user.
    - Saves the results as separate CSV files in organized folders under ../data/raw/.

Note:
    Ensure a valid `ms_token` is exported before running. The script is designed for manual use due to ms_token session limitations.
"""

from TikTokApi import TikTokApi
import asyncio
import os
import random
import datetime

import pandas as pd

cookies_list = [
    {
        "sessionid": "ad397154df2926ccec45777204a43378",  # Replace with actual values from TikTok
        "tt_webid": "1%7CsQnlsWZGj7mhbPo-R1BJ8Ob2Dq7TEdVXL_YoVpp38wQ%7C1747485012%7C520db60ec5eb78088b236a41351b959efca77c4e0657a433f77484382efbf20b",
        "sid_guard": "ad397154df2926ccec45777204a43378%7C1742977673%7C15551988%7CMon%2C+22-Sep-2025+08%3A27%3A41+GMT",
        # "csrf_session_id": "your_csrf_session_id",
        "tt_csrf_token": "Eaxav5Oa--VZmkd0_QOx1L4OYkXmpsD7psyA",
        # "passport_csrf_token": "e34822df36492895e854f8e56065d12a"

    }
]

# Set in terminal 
# export ms_token="ms_token_key"
ms_token = os.environ.get("ms_token", None)  # set your own ms_token

async def get_user_data(username="karishmaclimategirl", sleep_time=3):
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=sleep_time,
            browser="chromium",
            headless=False
        )

        try:
            print(f"\n=== Fetching Data for User: {username} ===")
            user = api.user(username)
            user_data = await user.info()
            
            # Extract relevant details
            user_info = user_data.get("userInfo", {}).get("user", {})
            stats = user_data.get("userInfo", {}).get("stats", {})

            user_dict = {
                "username": user_info.get("uniqueId", "N/A"),
                "verified": user_info.get("verified", False),
                "nickname": user_info.get("nickname", "N/A"),
                "bio": user_info.get("signature", "N/A"),
                "profile_link": user_info.get("bioLink", {}).get("link", "N/A"),
                "avatar": user_info.get("avatarThumb", "N/A"),
                "follower_count": stats.get("followerCount", 0),
                "following_count": stats.get("followingCount", 0),
                "video_count": stats.get("videoCount", 0),
                "total_likes": stats.get("heartCount", 0)
            }

            # Convert to pandas DataFrame
            df_user = pd.DataFrame([user_dict])
            print("\n=== User DataFrame ===")
            print(df_user)

            # Save as CSV
            csv_filename = f"../data/raw/user_profiles/tiktok_user_{username}.csv"
            os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
            df_user.to_csv(csv_filename, index=False)
            print(f"User data saved to {csv_filename}")
        
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None

        try:
            print("\n=== Fetching User Videos ===")
            video_count = user_dict.get("video_count", 0)  # Get video count dynamically
            videos_data = []
            async for video in user.videos(count=video_count):
                video_dict = video.as_dict
                videos_data.append({
                    "video_id": video_dict.get("id"),
                    "title": video_dict.get("desc"),
                    "likes": video_dict.get("stats", {}).get("diggCount"),
                    "comments": video_dict.get("stats", {}).get("commentCount"),
                    "shares": video_dict.get("stats", {}).get("shareCount"),
                    "views": video_dict.get("stats", {}).get("playCount"),
                    "timestamp": video_dict.get("createTime"),
                })
            
            # Convert to pandas DataFrame
            df_videos = pd.DataFrame(videos_data)
            print("\n=== User Videos DataFrame ===")
            print(df_videos)
            
            # Save videos as CSV
            videos_csv_filename = f"../data/raw/user_videos/tiktok_user_videos_{username}.csv"
            os.makedirs(os.path.dirname(videos_csv_filename), exist_ok=True)
            df_videos.to_csv(videos_csv_filename, index=False)
            print(f"User videos saved to {videos_csv_filename}")
        
        except Exception as e:
            print(f"Error fetching videos: {e}")


if __name__ == "__main__":
    asyncio.run(get_user_data())