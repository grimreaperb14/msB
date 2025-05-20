import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, vfx
import tempfile
import os
import requests
import yt_dlp

st.title("My AI Short Clips Editor")
st.write("Welcome to my Streamlit app!")

# -------------------------------
# Part 1: Upload Video & Edit
# -------------------------------

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

def process_video(input_path, start, end, speed, text):
    clip = VideoFileClip(input_path).subclip(start, end)

    # Speed control
    if speed != 1.0:
        clip = clip.fx(vfx.speedx, speed)

    # Add text overlay if text provided
    if text.strip():
        txt_clip = TextClip(text, fontsize=24, color='white', bg_color='black', method='caption')
        txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(clip.duration)
        clip = CompositeVideoClip([clip, txt_clip])

    return clip

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile.close()

    clip = VideoFileClip(tfile.name)
    st.video(tfile.name)

    start_time = st.number_input("Start time (seconds)", 0.0, clip.duration, 0.0)
    end_time = st.number_input("End time (seconds)", 0.0, clip.duration, clip.duration)
    speed = st.slider("Playback speed", 0.25, 3.0, 1.0, 0.05)
    overlay_text = st.text_input("Text overlay (leave blank for none)")

    if st.button("Process Uploaded Video"):
        if end_time > start_time:
            processed_clip = process_video(tfile.name, start_time, end_time, speed, overlay_text)
            out_path = os.path.join(tempfile.gettempdir(), "edited_video.mp4")
            processed_clip.write_videofile(out_path, codec='libx264')
            with open(out_path, 'rb') as f:
                st.download_button("Download Edited Video", f, file_name="edited_video.mp4")
        else:
            st.error("End time must be greater than start time.")

# -------------------------------
# Part 2: Download from URL & Edit
# -------------------------------

st.markdown("---")
st.title("Or paste YouTube or Direct Video URL here:")

video_url = st.text_input("Paste YouTube or direct video URL here:")

def download_youtube_video(url, output_path):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': f'{output_path}/downloaded_video.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_direct(url):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    r = requests.get(url, stream=True)
    with open(temp_file.name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return temp_file.name

if video_url:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            if "youtube.com" in video_url or "youtu.be" in video_url:
                download_youtube_video(video_url, temp_dir)
                video_path = os.path.join(temp_dir, "downloaded_video.mp4")
            else:
                video_path = download_direct(video_url)

            video = VideoFileClip(video_path)

            st.video(video_path)
            st.write(f"Video duration: {video.duration:.2f} seconds")

            start_time = st.number_input("Start time (seconds)", 0.0, video.duration, 0.0, key="url_start")
            end_time = st.number_input("End time (seconds)", 0.0, video.duration, video.duration, key="url_end")
            speed = st.slider("Playback speed", 0.25, 3.0, 1.0, 0.05, key="url_speed")
            overlay_text = st.text_input("Text overlay (leave blank for none)", key="url_text")

            if st.button("Process URL Video"):
                if end_time > start_time:
                    processed_clip = process_video(video_path, start_time, end_time, speed, overlay_text)
                    out_path = os.path.join(tempfile.gettempdir(), "edited_url_video.mp4")
                    processed_clip.write_videofile(out_path, codec='libx264')
                    with open(out_path, 'rb') as f:
                        st.download_button("Download Edited Video", f, file_name="edited_url_video.mp4")
                else:
                    st.error("End time must be greater than start time.")

    except Exception as e:
        st.error(f"Error downloading or processing video: {e}")

