"""
Script: get_video_comments.py

Description:
    This script fetches up to 700 comments from a specific TikTok video using the TikTokApi.
    It extracts relevant metadata such as comment text, author ID, likes, and timestamp, and
    saves the results as a CSV file in the appropriate user folder.

Usage:
    - Requires a valid `ms_token` to be set as an environment variable.
    - Optionally configure the browser type with TIKTOK_BROWSER.
    - Update the video_id and username path before running.

Output:
    A CSV file containing the comment data for the specified video.
"""

from TikTokApi import TikTokApi
import asyncio
import nest_asyncio
nest_asyncio.apply()
import os

import datetime
import pandas as pd

ms_token = os.environ.get("ms_token", None)  # set your own ms_token

async def get_comments(username, video_id):
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token], 
            num_sessions=1, 
            sleep_after=3, 
            browser=os.getenv("TIKTOK_BROWSER", "chromium")
        )
        
        video = api.video(id=video_id)
        comments_data = []
    
        print(f"\n=== Fetching Comments for Video ID: {video_id} ===")
        async for comment in video.comments(count=700):            
            comment_dict = comment.as_dict
            
            timestamp = comment_dict.get("create_time")
            formatted_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else "N/A"

            
            comments_data.append({
                "comment_id": comment_dict.get("cid"),
                "text": comment_dict.get("text"),
                "author_id": comment_dict.get("user", {}).get("id"),
                "author_username": comment_dict.get("user", {}).get("unique_id"),
                "likes": comment_dict.get("digg_count"),
                "reply_count": comment_dict.get("reply_comment_total"),
                "timestamp": formatted_time,

            })
            
        df_comments = pd.DataFrame(comments_data)
        print("\n=== Comments DataFrame ===")
        print(df_comments.head())
        print(df_comments.shape)
        
        # Save comments as CSV
        comments_csv_filename = f"../data/raw/comments/{username}/tiktok_comments_{video_id}.csv"
        df_comments.to_csv(comments_csv_filename, index=False)
        print(f"Comments saved to {comments_csv_filename}")
             
if __name__ == "__main__":
    asyncio.run(get_comments(
        username = "climatediva",
        video_id = 7505065575429836062
    ))