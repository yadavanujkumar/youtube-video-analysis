import re
import os
import uuid
from pytube import YouTube
import logging
import yt_dlp


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
    
    def download_audio(self, url):
        """Download the audio track from the YouTube video."""
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                raise Exception("No audio stream available for this video")
            
            # Create a unique filename
            filename = f"{uuid.uuid4()}.mp3"
            output_path = os.path.join(self.temp_dir, filename)
            
            # Download the audio
            audio_stream.download(output_path=self.temp_dir, filename=filename)
            
            self.logger.info(f"Audio downloaded: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error downloading audio: {str(e)}")
            raise Exception(f"Failed to download audio: {str(e)}")
    
    def cleanup(self, file_path):
        """Clean up temporary files."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Deleted temporary file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up file {file_path}: {str(e)}")
