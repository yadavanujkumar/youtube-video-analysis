from flask import Flask, render_template, request, jsonify
from youtube_processor import YouTubeProcessor
from transcription import Transcriber
from understanding import ContentAnalyzer
from query_processor import QueryProcessor
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Initialize components
youtube_processor = YouTubeProcessor()
transcriber = Transcriber()
content_analyzer = ContentAnalyzer()
query_processor = QueryProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.json
    youtube_url = data.get('youtube_url')
    
    # Validate YouTube URL
    if not youtube_processor.is_valid_youtube_url(youtube_url):
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    try:
        # Extract video information
        video_info = youtube_processor.extract_video_info(youtube_url)
        
        # Download audio
        audio_path = youtube_processor.download_audio(youtube_url)
        
        # Transcribe audio
        transcript = transcriber.transcribe(audio_path)
        
        # Analyze content
        analysis = content_analyzer.analyze(transcript, video_info)
        
        # Clean up temporary files
        youtube_processor.cleanup(audio_path)
        
        return jsonify({
            "video_id": video_info["video_id"],
            "title": video_info["title"],
            "status": "processed",
            "message": f"Successfully processed video: {video_info['title']}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    video_id = data.get('video_id')
    query_text = data.get('query')
    
    if not video_id or not query_text:
        return jsonify({"error": "Missing video_id or query"}), 400
    
    try:
        # Get analysis for the video
        analysis = content_analyzer.get_analysis(video_id)
        
        # Process the query
        response = query_processor.process_query(query_text, analysis)
        
        return jsonify({
            "response": response,
            "video_id": video_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/video_details/<video_id>', methods=['GET'])
def video_details(video_id):
    try:
        # Look up the video details from our saved analysis
        analysis_path = os.path.join(content_analyzer.analysis_dir, f"{video_id}.json")
        
        if not os.path.exists(analysis_path):
            # If we don't have an analysis yet, get basic info from YouTube
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            return jsonify({
                "video_id": video_id,
                "title": yt.title,
                "description": yt.description,
                "author": yt.author,
                "thumbnail_url": yt.thumbnail_url
            })
        
        # If we have an analysis, return the video info from there
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)
            return jsonify(analysis["video_info"])
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)