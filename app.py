import streamlit as st
import yt_dlp
import os
import uuid
import re
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.markdown("""
<h1 style='display: flex; align-items: center; gap: 10px;'>
  <svg xmlns="http://www.w3.org/2000/svg" height="28" viewBox="0 0 576 512" fill="red">
    <path d="M549.7 124.1c-6.3-23.8-25-42.5-48.9-48.9C458.6 64 288 64 288 64S117.4 64 75.2 75.2c-23.9 6.3-42.6 25-48.9 48.9
    C16 166.3 16 256 16 256s0 89.7 10.3 131.9c6.3 23.8 25 42.5 48.9 48.9C117.4 448 288 448 288 448s170.6 0 212.8-11.2
    c23.9-6.3 42.6-25 48.9-48.9C560 345.7 560 256 560 256s0-89.7-10.3-131.9zM232 334V178l142 78-142 78z"/>
  </svg>
  YouTube Video Downloader
</h1>
""", unsafe_allow_html=True)

url = st.text_input("Enter YouTube Video URL")

# User choice: Windows or Android
os_choice = st.radio("Select your OS", ["Windows", "Android"])

# User choice: Video or Audio
download_type = st.radio("Select download type", ["Video", "Audio"])

start_time, end_time = None, None
if download_type == "Audio":
    st.info("Optional: Enter timestamps (HH:MM:SS format) to trim audio.")
    start_time = st.text_input("Start Time (e.g., 00:01:30)", "")
    end_time = st.text_input("End Time (e.g., 00:03:45)", "")

# Loader placeholders
loading_placeholder = st.empty()
thumbnail_placeholder = st.empty()
button_placeholder = st.empty()

loader_css = """<style> ... </style>"""  # keep your loader CSS
loader_html = "<div class='loader'></div><p style='text-align:center;'>Your video is loading. This might take a moment...</p>"

def validate_time_format(t: str) -> bool:
    if not t:
        return True
    try:
        datetime.strptime(t, "%H:%M:%S")
        return True
    except ValueError:
        return False

def convert_to_seconds(t: str) -> int:
    if not t:
        return None
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

if url:
    # Validate timestamps if audio mode
    if download_type == "Audio":
        if not validate_time_format(start_time):
            st.error("❌ Invalid Start Time format. Use HH:MM:SS.")
            st.stop()
        if not validate_time_format(end_time):
            st.error("❌ Invalid End Time format. Use HH:MM:SS.")
            st.stop()

        if start_time and end_time:
            start_sec = convert_to_seconds(start_time)
            end_sec = convert_to_seconds(end_time)
            if end_sec <= start_sec:
                st.error("❌ End time must be greater than Start time.")
                st.stop()

    loading_placeholder.markdown(loader_css + loader_html, unsafe_allow_html=True)

    file_id = str(uuid.uuid4())
    output_path = f"{file_id}.%(ext)s"

    if download_type == "Video":
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'quiet': True,
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        if start_time or end_time:
            start_sec = convert_to_seconds(start_time)
            end_sec = convert_to_seconds(end_time)
            ydl_opts['download_ranges'] = lambda info_dict, ydl: [{
                'start_time': start_sec if start_sec else 0,
                'end_time': end_sec if end_sec else None
            }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'video')
            yt_id = info_dict.get('id', None)

        loading_placeholder.empty()
        st.success("✅ Download complete!")

        if yt_id:
            thumbnail_url = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            thumbnail_placeholder.image(thumbnail_url, use_container_width=True)

        ext = "mp4" if download_type == "Video" else "mp3"
        final_file = f"{file_id}.{ext}"

        # Download button
        with open(final_file, "rb") as file:
            button_placeholder.download_button(
                label=f"📥 Download {download_type}",
                data=file,
                file_name=f"{title}.{ext}",
                mime="audio/mpeg" if ext == "mp3" else "video/mp4"
            )

        # If OS is Android → also dump to Downloads
        if os_choice == "Android":
            downloads_path = str(Path.home() / "Downloads" / f"{title}.{ext}")
            os.replace(final_file, downloads_path)
            st.success(f"📂 Saved to Downloads: {downloads_path}")
        else:
            os.remove(final_file)

    except Exception as e:
        loading_placeholder.empty()
        st.error(f"❌ Error: {e}")
