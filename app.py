import streamlit as st
import yt_dlp
import os
import re
from datetime import datetime

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.markdown("""
<h1 style='display: flex; align-items: center; gap: 10px;'>
  <svg xmlns="http://www.w3.org/2000/svg" height="28" viewBox="0 0 576 512" fill="red">
    <path d="M549.7 124.1c-6.3-23.8-25-42.5-48.9-48.9C458.6 64 288 64 288 64S117.4 64 75.2 75.2c-23.9 6.3-42.6-25-48.9 48.9
    C16 166.3 16 256 16 256s0 89.7 10.3 131.9c6.3 23.8 25 42.5 48.9 48.9C117.4 448 288 448 288 448s170.6 0 212.8-11.2
    c23.9-6.3 42.6-25 48.9-48.9C560 345.7 560 256 560 256s0-89.7-10.3-131.9zM232 334V178l142 78-142 78z"/>
  </svg>
  YouTube Video Downloader
</h1>
""", unsafe_allow_html=True)

# Inputs
url = st.text_input("Enter YouTube Video URL")
download_type = st.radio("Select download type", ["Video", "Audio"])
os_choice = st.radio("Select your OS", ["Windows", "Android"])

start_time, end_time = None, None
if download_type == "Audio":
    st.info("Optional: Enter timestamps (HH:MM:SS format) to trim audio.")
    start_time = st.text_input("Start Time (e.g., 00:01:30)", "")
    end_time = st.text_input("End Time (e.g., 00:03:45)", "")

# Helpers
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

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\\-_\\. ]', '_', name)

# Main logic
if url:
    # Validate time inputs
    if download_type == "Audio":
        if not validate_time_format(start_time):
            st.error("❌ Invalid Start Time format.")
            st.stop()
        if not validate_time_format(end_time):
            st.error("❌ Invalid End Time format.")
            st.stop()
        if start_time and end_time:
            start_sec = convert_to_seconds(start_time)
            end_sec = convert_to_seconds(end_time)
            if end_sec <= start_sec:
                st.error("❌ End time must be greater than Start time.")
                st.stop()

    # yt-dlp options
    if download_type == "Video":
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': '%(id)s.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': True,
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(id)s.%(ext)s',
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
            yt_id = info_dict.get('id')
            downloaded_file = ydl.prepare_filename(info_dict)  # ✅ actual file name from yt-dlp

        st.success("✅ Download complete!")

        # Fix safe file name
        safe_title = sanitize_filename(title)
        ext = "mp4" if download_type == "Video" else "mp3"
        target_name = f"{safe_title}.{ext}"

        if os_choice == "Android":
            downloads_path = f"/storage/shared/Downloads/{target_name}"
            try:
                os.replace(downloaded_file, downloads_path)
                st.success(f"📂 Saved to Android Downloads:\n{downloads_path}")
            except Exception as e:
                st.error(f"❌ Could not move file to Downloads: {e}")
        else:
            with open(downloaded_file, "rb") as file:
                st.download_button(
                    label=f"📥 Download {download_type}",
                    data=file,
                    file_name=target_name,
                    mime="audio/mpeg" if ext == "mp3" else "video/mp4"
                )
            os.remove(downloaded_file)

    except Exception as e:
        st.error(f"❌ Error: {e}")
