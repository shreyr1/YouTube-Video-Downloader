
import streamlit as st
import yt_dlp
import os
import uuid
import re

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

# Predefine containers so layout doesn't jump
loading_placeholder = st.empty()
thumbnail_placeholder = st.empty()
button_placeholder = st.empty()

loader_css = """
<style>
.loader {
    position: relative;
    width: 108px;
    height: 48px; /* Lock height to prevent layout jump */
    display: flex;
    justify-content: space-between;
    margin: 30px auto;
}
.loader::after, .loader::before {
    content: '';
    display: inline-block;
    width: 48px;
    height: 48px;
    background-color: #FFF;
    background-image: radial-gradient(circle 14px, #0d161b 100%, transparent 0);
    background-repeat: no-repeat;
    border-radius: 50%;
    animation: eyeMove 10s infinite, blink 10s infinite;
    transform-origin: center;
}
@keyframes eyeMove {
    0%, 10% { background-position: 0px 0px; }
    13%, 40% { background-position: -15px 0px; }
    43%, 70% { background-position: 15px 0px; }
    73%, 90% { background-position: 0px 15px; }
    93%, 100% { background-position: 0px 0px; }
}
@keyframes blink {
    0%, 10%, 12%, 20%, 22%, 40%, 42%, 60%, 62%, 70%, 72%, 90%, 92%, 98%, 100% {
        transform: scaleY(1);
    }
    11%, 21%, 41%, 61%, 71%, 91%, 99% {
        transform: scaleY(0.4); /* Simulate blinking without changing height */
    }
}
</style>
"""


loader_html = "<div class='loader'></div><p style='text-align:center;'>Your video is loading. This might take a moment...</p>"

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

if url:
    # Show loader immediately
    loading_placeholder.markdown(loader_css + loader_html, unsafe_allow_html=True)

    video_id = str(uuid.uuid4())
    output_path = f"{video_id}.mp4"

    ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    'outtmpl': output_path,
    'merge_output_format': 'mp4',
    'quiet': True,
}


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'video')
            yt_id = info_dict.get('id', None)

        # Clean up loader once video is ready
        loading_placeholder.empty()

        st.success("✅ Download complete!")

        # Show thumbnail
        if yt_id:
            thumbnail_url = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            thumbnail_placeholder.image(thumbnail_url, use_container_width=True)

        # Show download button
        with open(output_path, "rb") as file:
            button_placeholder.download_button(
                label="📥 Download Video",
                data=file,
                file_name=f"{title}.mp4",
                mime="video/mp4"
            )

        os.remove(output_path)

    except Exception as e:
        loading_placeholder.empty()
        st.error(f"❌ Error: {e}")
