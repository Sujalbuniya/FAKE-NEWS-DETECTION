from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

class FakeNewsModel:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
            ('clf', LogisticRegression(random_state=42))
        ])
        self.initialize_model()
        
    def initialize_model(self):
        """Initialize with some basic examples"""
        X_train = [
            "Scientists discover new species in Amazon rainforest",
            "Breaking: Alien invasion happening right now",
            "President signs new climate change legislation",
            "Secret cure for cancer discovered but hidden by government",
            "Economic indicators show steady growth this quarter",
            "Celebrity spotted with extraterrestrial being"
        ]
        y_train = [1, 0, 1, 0, 1, 0]  # 1 = real, 0 = fake
        
        self.pipeline.fit(X_train, y_train)
    
    def predict(self, text):
        """
        Predict whether text is fake news
        Returns probability of being real news
        """
        try:
            proba = self.pipeline.predict_proba([text])
            return proba[0][1]
        except:
            return 0.5