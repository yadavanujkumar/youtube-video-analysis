import re
import os
import uuid
from pytube import YouTube
import logging
import yt_dlp
import traceback


class YouTubeProcessor:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def is_valid_youtube_url(self, url):
        """Check if the provided URL is a valid YouTube URL."""
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        match = re.match(youtube_regex, url)
        return match is not None
    

# Replace the extract_video_info method
    def extract_video_info(self, url):
        """Extract basic information about the YouTube video using yt-dlp."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'format': 'bestaudio'
            }
        
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            return {
                "video_id": info.get('id'),
                "title": info.get('title'),
                "description": info.get('description') or "No description available",
                "length": info.get('duration'),
                "author": info.get('uploader'),
                "publish_date": info.get('upload_date'),
                "views": info.get('view_count'),
                "thumbnail_url": info.get('thumbnail')
            }
        except Exception as e:
            self.logger.error(f"Error extracting video info: {str(e)}")
            raise Exception(f"Failed to extract video information: {str(e)}")

    def download_audio(self, url: str) -> str:
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio/%(title)s.%(ext)s',  # Save to "audio" folder
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
                'verbose': True,  # Debugging logs
                'cookiefile': 'cookies.txt',  # For restricted videos
                'ffmpeg_location': r'C:\Program Files\ffmpeg-7.1.1-essentials_build\bin',  # Path to FFmpeg
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info).replace(".webm", ".mp3")

        except Exception as e:
            print(f"Error: {str(e)}\n{traceback.format_exc()}")
            raise
        
    def cleanup(self, file_path):
        """Clean up temporary files."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Deleted temporary file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up file {file_path}: {str(e)}")
