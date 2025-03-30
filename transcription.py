import os
import json
from datetime import datetime
import openai
import logging

class Transcriber:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.transcripts_dir = os.path.join(os.getcwd(), 'transcripts')
        if not os.path.exists(self.transcripts_dir):
            os.makedirs(self.transcripts_dir)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def transcribe(self, audio_path):
        """Transcribe audio file using OpenAI's Whisper API."""
        try:
            self.logger.info(f"Starting transcription for: {audio_path}")
            
            with open(audio_path, "rb") as audio_file:
                response = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            # Extract transcript and metadata
            transcript = {
                "text": response["text"],
                "segments": response.get("segments", []),
                "timestamp": datetime.now().isoformat(),
                "audio_path": audio_path
            }
            
            # Save transcript to file
            video_id = os.path.basename(audio_path).split('.')[0]
            transcript_path = os.path.join(self.transcripts_dir, f"{video_id}.json")
            
            with open(transcript_path, 'w') as f:
                json.dump(transcript, f, indent=2)
            
            self.logger.info(f"Transcription completed and saved to: {transcript_path}")
            return transcript
        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")

