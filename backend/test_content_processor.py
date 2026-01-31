import logging
import sys
from agents.content_processor import ContentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    print("--- Starting Content Processor Test (Gemini API) ---")
    
    # 1. Initialize Processor
    # API Key is autoloaded from .env
    try:
        processor = ContentProcessor()
        print("[OK] Processor initialized.")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        return

    # 2. Mock Article
    dummy_articles = [{
        'title': 'New Breakthrough in Solid State Batteries Announced by Toyota',
        'source': 'TechDaily',
        'link': 'http://example.com/battery-news',
        'genre': 'new_tech'
    }]
    
    print(f"Processing article: {dummy_articles[0]['title']}")

    # 3. Process
    try:
        results = processor.process(dummy_articles)
        
        if results:
            print("\n[SUCCESS] Processing Complete!")
            result = results[0]
            print(f"Title: {result['title']}")
            print(f"Score: {result['score']}/10")
            print("Summary:")
            print(result['summary'])
        else:
            print("\n[FAILURE] No results returned (Check API Key or Quota).")
            
    except Exception as e:
        print(f"\n[ERROR] Processing failed: {e}")

if __name__ == "__main__":
    main()
