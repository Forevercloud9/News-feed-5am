import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Content processing will fail.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash') # Using Flash for speed/cost

    def process(self, articles):
        """
        Process a list of articles: Summarize and Score.
        Returns a list of processed article objects.
        """
        if not self.api_key:
            logger.error("Skipping processing due to missing API Key.")
            return []

        processed_results = []
        
        # Batch processing or individual? 
        # For better quality, individual or small batches are better. 
        # Let's do a loop for MVP (optimization: parallelize later).
        
        for article in articles:
            try:
                result = self._summarize_article(article)
                if result:
                    processed_results.append(result)
            except Exception as e:
                logger.error(f"Failed to process article {article['title']}: {e}")
        
        return processed_results

    def _summarize_article(self, article):
        prompt = f"""
        You are a professional news analyst. Summarize the following news article into exactly 3 bullet points (Japanese).
        Also, assign a "Reliability Score" from 1 to 10 based on the source and content clarity.
        
        Title: {article['title']}
        Source: {article['source']}
        
        Output format:
        Summary: 
        - Point 1
        - Point 2
        - Point 3
        Score: X/10
        """
        
        # In a real app, we would fetch the full content of the article using 'article['link']'.
        # For this MVP, we are summarizing based on the Title (and snippet if available) 
        # because scraping full content is complex/timely.
        # We will assume the title gives enough context for a "Headlines" summary.
        
        response = self.model.generate_content(prompt)
        text = response.text
        
        # Simple parsing (robust parsing would use JSON mode)
        summary = "No summary available."
        score = 5
        
        try:
            lines = text.split('\n')
            summary_lines = [l for l in lines if l.strip().startswith('-') or l.strip().startswith('•')]
            summary = "\n".join(summary_lines[:3]) # Take top 3
            
            # Extract score
            for line in lines:
                if 'Score:' in line:
                    score_part = line.split('Score:')[1].strip().split('/')[0]
                    score = int(score_part)
        except:
            pass

        return {
            'title': article['title'],
            'link': article['link'],
            'summary': summary,
            'score': score,
            'genre': article['genre'],
            'source': article['source']
        }

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    processor = ContentProcessor()
    dummy_article = {
        'title': 'Japan Tobacco announces new investment strategy for 2026',
        'source': 'Reuters',
        'link': 'http://example.com',
        'genre': 'corporate_tracking'
    }
    print(processor.process([dummy_article]))
