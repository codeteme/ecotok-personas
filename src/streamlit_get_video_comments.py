import streamlit as st
from TikTokApi import TikTokApi
import asyncio
import asyncio.subprocess
# Suppress subprocess transport cleanup errors in closed loops
asyncio.subprocess.BaseSubprocessTransport.__del__ = lambda self: None
import nest_asyncio
nest_asyncio.apply()
import os
import datetime
import pandas as pd

st.set_page_config(page_title="TikTok Comments Downloader", layout="centered")

st.title("TikTok Video Comments Downloader")

# --- Sidebar inputs ---
st.sidebar.header("Configuration")
ms_token = st.sidebar.text_input("ms_token", type="password", help="Your TikTok ms_token")
username = st.sidebar.text_input("Username", help="Used to name the output folder")
video_id = st.sidebar.text_input("Video ID", help="ID of the TikTok video")

# --- Fetch function ---
async def _get_comments(ms_token: str, video_id: str):
    os.environ["ms_token"] = ms_token  # ensure TikTokApi picks it up
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "chromium")
        )
        video = api.video(id=video_id)
        comments = []
        async for comment in video.comments(count=700):
            d = comment.as_dict
            ts = d.get("create_time")
            ts_fmt = (datetime.datetime.fromtimestamp(ts)
                      .strftime("%Y-%m-%d %H:%M:%S")) if ts else "N/A"
            comments.append({
                "comment_id": d.get("cid"),
                "text": d.get("text"),
                "author_id": d.get("user", {}).get("id"),
                "author_username": d.get("user", {}).get("unique_id"),
                "likes": d.get("digg_count"),
                "reply_count": d.get("reply_comment_total"),
                "timestamp": ts_fmt,
            })
        return pd.DataFrame(comments)


# Updated fetch_comments with event loop handling
def fetch_comments(ms_token: str, video_id: str) -> pd.DataFrame:
    """
    Run the async _get_comments coroutine, but handle
    already-running event loops inside Streamlit.
    """
    try:
        # Check if there's an existing running event loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop: safe to use asyncio.run()
        return asyncio.run(_get_comments(ms_token, video_id))
    else:
        # Running inside Streamlit: create and manage a separate loop
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_get_comments(ms_token, video_id))
        finally:
            loop.close()

# --- Main UI ---
if st.sidebar.button("Fetch Comments"):
    if not (ms_token and username and video_id):
        st.sidebar.error("Please fill in all fields above")
    else:
        with st.spinner("Fetching comments..."):
            try:
                df = fetch_comments(ms_token, video_id)
                st.success(f"Fetched {len(df)} comments!")
                st.dataframe(df.head())
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{username}_tiktok_comments_{video_id}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error: {e}")