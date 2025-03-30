import openai
import os
import logging

class QueryProcessor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_query(self, query, analysis):
        """Process user query against video analysis."""
        try:
            self.logger.info(f"Processing query: {query}")
            
            # Extract relevant information
            video_info = analysis.get("video_info", {})
            analysis_content = analysis.get("analysis", {})
            
            # Create a prompt for the LLM
            prompt = f"""
            I need you to answer a question about a YouTube video based on its analysis.
            
            VIDEO INFORMATION:
            Title: {video_info.get('title', 'Unknown')}
            Creator: {video_info.get('author', 'Unknown')}
            
            VIDEO ANALYSIS:
            Summary: {analysis_content.get('summary', 'Not available')}
            
            Main Topics: {', '.join(analysis_content.get('topics', ['Not available']))}
            
            Key Points:
            {', '.join(analysis_content.get('key_points', ['Not available']))}
            
            Timeline:
            {analysis_content.get('timeline', 'Not available')}
            
            Entities Mentioned:
            {', '.join(analysis_content.get('entities', ['Not available']))}
            
            USER QUERY:
            {query}
            
            Please provide a concise and accurate answer to the user's query based on the video content.
            If you can't answer the query based on the available information, please say so clearly.
            """
            
            # Use OpenAI to process the query
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions about YouTube videos based on their content analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            # Extract the response
            answer = response.choices[0].message.content
            
            self.logger.info(f"Query processed successfully")
            return answer
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise Exception(f"Failed to process query: {str(e)}")