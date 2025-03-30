import os
import json
import openai
import logging
from datetime import datetime

class ContentAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.analysis_dir = os.path.join(os.getcwd(), 'analysis')
        if not os.path.exists(self.analysis_dir):
            os.makedirs(self.analysis_dir)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, transcript, video_info):
        """Analyze transcript to understand the content."""
        try:
            transcript_text = transcript["text"]
            video_id = video_info["video_id"]
            
            self.logger.info(f"Starting content analysis for video: {video_id}")
            
            # Create a prompt for the LLM
            prompt = f"""
            I need a comprehensive analysis of the following YouTube video transcript:
            
            Video Title: {video_info['title']}
            Video Author: {video_info['author']}
            
            TRANSCRIPT:
            {transcript_text}
            
            Please provide the following:
            1. A concise summary of the video
            2. Main topics discussed
            3. Key points and insights
            4. Timeline with major sections/topics and their timestamps
            5. Entities mentioned (people, organizations, products, etc.)
            
            Format the response as a structured JSON.
            """
            
            # Use OpenAI to analyze the content
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert content analyst specializing in extracting meaningful information from video transcripts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Extract the analysis content
            analysis_text = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                analysis_json = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If the response is not valid JSON, create a structured dict
                analysis_json = {
                    "summary": analysis_text,
                    "topics": [],
                    "key_points": [],
                    "timeline": [],
                    "entities": []
                }
            
            # Add metadata
            analysis = {
                "video_id": video_id,
                "analysis": analysis_json,
                "timestamp": datetime.now().isoformat(),
                "video_info": video_info
            }
            
            # Save analysis to file
            analysis_path = os.path.join(self.analysis_dir, f"{video_id}.json")
            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            self.logger.info(f"Content analysis completed and saved to: {analysis_path}")
            return analysis
        except Exception as e:
            self.logger.error(f"Error during content analysis: {str(e)}")
            raise Exception(f"Content analysis failed: {str(e)}")
    
    def get_analysis(self, video_id):
        """Retrieve the analysis for a given video ID."""
        try:
            analysis_path = os.path.join(self.analysis_dir, f"{video_id}.json")
            
            if not os.path.exists(analysis_path):
                raise FileNotFoundError(f"Analysis not found for video ID: {video_id}")
            
            with open(analysis_path, 'r') as f:
                analysis = json.load(f)
            
            return analysis
        except Exception as e:
            self.logger.error(f"Error retrieving analysis: {str(e)}")
            raise Exception(f"Failed to retrieve analysis: {str(e)}")
