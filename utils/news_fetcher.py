from newspaper import Article

class NewsFetcher:
    def __init__(self):
        self.trusted_sources = [
            'reuters.com', 'apnews.com', 'bbc.com', 'npr.org', 
            'theguardian.com', 'nytimes.com', 'wsj.com', 'washingtonpost.com'
        ]
        
    def fetch_news_from_api(self, query, count=10):
        """
        Fetch news from News API
        """
        try:
            print(f"Would fetch news for query: {query}")
            return []
        except Exception as e:
            print(f"Error fetching news from API: {e}")
            return []
    
    def extract_article_content(self, url):
        """
        Extract main content from a news article URL
        """
        try:
            article = Article(url)
            article.download()
            article.parse()
            return {
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'source': url.split('/')[2]
            }
        except Exception as e:
            print(f"Error extracting article content: {e}")
            return None
    
    def get_multiple_perspectives(self, claim, max_articles=5):
        """
        Get multiple perspectives on a claim from different sources
        """
        articles = self.fetch_news_from_api(claim, max_articles * 2)
        perspectives = []
        
        for article in articles:
            if article.get('url'):
                content = self.extract_article_content(article['url'])
                if content and content['text']:
                    perspectives.append(content)
                    if len(perspectives) >= max_articles:
                        break
        
        return perspectives