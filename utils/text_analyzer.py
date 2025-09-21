import re
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords

# Download required NLTK data
nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)

class TextAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.sensational_words = [
            'shocking', 'astonishing', 'unbelievable', 'miracle', 'secret',
            'they don\'t want you to know', 'breaking', 'exclusive', 'virality'
        ]
    
    def calculate_sensationalism_score(self, text):
        """
        Calculate a score indicating how sensationalist the text is
        """
        text_lower = text.lower()
        score = 0
        
        # Check for sensational words
        for word in self.sensational_words:
            if word in text_lower:
                score += 1
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            score += min(exclamation_count / 3, 5)
            
        # Check for all caps
        all_caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        score += len(all_caps_words) * 0.5
        
        return min(score, 10)
    
    def analyze_sentiment(self, text):
        """
        Analyze the sentiment of the text
        """
        sentiment_scores = self.sia.polarity_scores(text)
        return sentiment_scores
    
    def calculate_subjectivity_score(self, text):
        """
        Calculate how subjective the text is
        """
        blob = TextBlob(text)
        return blob.sentiment.subjectivity
    
    def extract_key_claims(self, text):
        """
        Extract key claims from the text
        """
        sentences = re.split(r'[.!?]+', text)
        claims = [s.strip() for s in sentences if len(s.split()) > 5 and len(s.split()) < 30]
        return claims[:5]