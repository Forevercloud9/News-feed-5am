import feedparser
import logging
import datetime

logger = logging.getLogger(__name__)

class NewsAggregator:
    def __init__(self):
        self.base_url = "https://news.google.com/rss"
        # Define feeds/queries for each genre
        self.feeds = {
            'domestic_business': {'url': f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWvfSkdnZ0YwWjI0Y1hDNW1iVzVvYkNnQVAB?hl=ja&gl=JP&ceid=JP:ja", 'lang': 'ja'}, # Business JP
            'global_business': {'url': f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWvfSkdnZ0YwWjI0Y1hDNW1iVzVvYkNnQVAB?hl=en-US&gl=US&ceid=US:en", 'lang': 'en'}, # Business US
            'finance': {'query': 'Finance+Market+Economy', 'lang': 'ja'},
            'global_tech': {'url': f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWvfSkdnZ0YwWjI0Y1hDNW1iVzVvYkNnQVAB?hl=en-US&gl=US&ceid=US:en", 'query': 'Technology'}, # Tech US logic needs checking, using search for simplicity? No, use topic.
            'new_tech': {'query': 'Artificial+Intelligence+New+Technology', 'lang': 'en'},
            'corporate_tracking': {'query': 'Japan+Tobacco+British+American+Tobacco', 'lang': 'ja'},
            'entertainment': {'query': 'Music+Festival+Market', 'lang': 'ja'},
            'sports': {'query': 'Shohei+Ohtani+Baseball', 'lang': 'ja'},
            'science': {'query': 'Science+Discovery+Space', 'lang': 'en'},
            'health': {'query': 'Health+Wellness+Medical+News', 'lang': 'ja'},
            'politics': {'query': 'Japan+Politics+Government', 'lang': 'ja'},
            'startups': {'query': 'Startup+Venture+Capital+Japan', 'lang': 'ja'},
        }
        # Note: For 'topics', we use the direct topic URL. For 'queries', we build the search URL.
    
    def _build_search_url(self, query, lang='ja'):
        ceid = 'JP:ja' if lang == 'ja' else 'US:en'
        hl = 'ja' if lang == 'ja' else 'en-US'
        gl = 'JP' if lang == 'ja' else 'US'
        return f"{self.base_url}/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"

    def collect_news(self, selected_genres=None, custom_topics=None):
        """
        Collects news for the selected genres AND custom user topics.
        :param selected_genres: List of keys to collect (e.g., ['domestic_business', 'finance']). 
        :param custom_topics: List of strings (e.g., ["SpaceX", "Ramen"]).
        """
        articles = []
        target_keys = selected_genres if selected_genres else self.feeds.keys()

        logger.info(f"Starting news collection. Genres: {target_keys}, Custom: {custom_topics}")

        # 1. Collect Standard Genres
        for key in target_keys:
            if key not in self.feeds:
                continue
            
            config = self.feeds[key]
            
            # Determine URL
            if 'url' in config and 'query' not in config:
                feed_url = config['url']
            else:
                query = config.get('query', 'News')
                feed_url = self._build_search_url(query, config.get('lang', 'ja'))
            
            self._fetch_and_append(feed_url, articles, genre_label=key)

        # 2. Collect Custom Topics
        if custom_topics:
            for topic in custom_topics:
                if not topic.strip(): continue
                # Assume Japanese context for custom topics unless detected otherwise? Default to JP for now.
                feed_url = self._build_search_url(topic, 'ja')
                self._fetch_and_append(feed_url, articles, genre_label=f"Custom: {topic}")
        
        logger.info(f"Collected {len(articles)} articles in total.")
        return articles

    def _fetch_and_append(self, feed_url, articles_list, genre_label):
        """Helper to fetch feed and append to list"""
        try:
            feed = feedparser.parse(feed_url)
            # Extract top 3 entries per category (reduced from 5 to avoid overload with many categories)
            for entry in feed.entries[:3]:
                articles_list.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', datetime.datetime.now().isoformat()),
                    'source': entry.get('source', {}).get('title', 'Unknown'),
                    'genre': genre_label
                })
        except Exception as e:
            logger.error(f"Error fetching feed {genre_label}: {e}")

if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    ag = NewsAggregator()
    news = ag.collect_news(['corporate_tracking', 'domestic_business'])
    for n in news:
        print(f"[{n['genre']}] {n['title']}")
