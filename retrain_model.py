# retrain_model.py (place in root folder)
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.utils import resample
import pickle
import os
import sys

# Add the current directory to Python path so we can import from utils
sys.path.append('.')

def download_nltk_data():
    """Download required NLTK data"""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

def load_and_balance_data():
    """Load and balance the dataset"""
    # Try different possible data file locations
    possible_paths = [
        'data/news_data.csv',
        'data/data.csv', 
        'news_data.csv',
        'data.csv'
    ]
    
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"Loaded data from: {path}")
            break
    
    if df is None:
        # Create sample data if no file found
        print("No data file found. Creating sample data...")
        return create_sample_data()
    
    print("Original class distribution:")
    print(df['label'].value_counts())
    
    # Balance the dataset
    df_real = df[df['label'] == 0]
    df_fake = df[df['label'] == 1]
    
    # Upsample minority class
    if len(df_fake) < len(df_real):
        df_fake_upsampled = resample(df_fake, 
                                    replace=True, 
                                    n_samples=len(df_real), 
                                    random_state=42)
        df_balanced = pd.concat([df_real, df_fake_upsampled])
    else:
        df_real_upsampled = resample(df_real, 
                                    replace=True, 
                                    n_samples=len(df_fake), 
                                    random_state=42)
        df_balanced = pd.concat([df_real_upsampled, df_fake])
    
    print("\nBalanced class distribution:")
    print(df_balanced['label'].value_counts())
    
    return df_balanced

def create_sample_data():
    """Create sample balanced data if no dataset exists"""
    sample_data = {
        'title': [
            "Aliens Invade New York City",
            "Chocolate Cures All Diseases",
            "Government Controls Weather",
            "Celebrity Spots Mythical Creature", 
            "Miracle Drug Extends Life to 500 Years",
            "City Council Approves Budget",
            "School District Announces Initiatives",
            "Researchers Study Climate Change",
            "Company Reports Quarterly Earnings",
            "Community Organizes Clean-up Event"
        ],
        'text': [
            "Aliens have landed in New York and are taking over the city in a spectacular invasion.",
            "Scientists discover that eating chocolate instantly cures all known diseases worldwide.",
            "The government has been secretly controlling weather patterns across the globe for years.",
            "Famous celebrity was spotted playing with a unicorn in their backyard yesterday.",
            "New miracle drug discovered that allows humans to live for 500 years without aging.",
            "The city council has approved a new budget focused on public transportation improvements.",
            "Local school district announces new educational initiatives for the upcoming academic year.",
            "University researchers are studying the effects of climate change on coastal communities.",
            "Major corporation reports strong quarterly earnings and positive growth projections.",
            "Community volunteers organize neighborhood clean-up event for this weekend."
        ],
        'label': [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]  # 1=Fake, 0=Real
    }
    
    df = pd.DataFrame(sample_data)
    print("Created sample data with balanced classes")
    return df

def preprocess_text(text):
    """Clean and preprocess text"""
    if pd.isna(text):
        return ""
    
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    
    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    
    return ' '.join(words)

def train_new_model():
    """Train a new model with balanced data"""
    print("=== FAKE NEWS MODEL RETRAINING ===")
    
    # Download NLTK data
    download_nltk_data()
    
    # Load and prepare data
    print("1. Loading and preparing data...")
    df = load_and_balance_data()
    
    # Preprocess text
    print("2. Preprocessing text...")
    df['cleaned_text'] = df['text'].apply(preprocess_text)
    
    # Create TF-IDF features
    print("3. Creating features...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8,
        stop_words='english'
    )
    
    X = tfidf.fit_transform(df['cleaned_text'])
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train multiple models to find the best one
    print("4. Training models...")
    
    models = {
        'Logistic Regression': LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42),
    }
    
    best_model = None
    best_name = None
    best_accuracy = 0
    
    for name, model in models.items():
        print(f"   Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"   {name} Accuracy: {accuracy:.3f}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_name = name
    
    print(f"\n5. Best model: {best_name} with accuracy: {best_accuracy:.3f}")
    
    # Save the best model and vectorizer
    models_dir = 'models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    with open('models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(tfidf, f)
    
    with open('models/fake_news_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    
    print("\n=== MODEL TRAINING COMPLETE ===")
    print("✓ New model saved to: models/fake_news_model.pkl")
    print("✓ Vectorizer saved to: models/tfidf_vectorizer.pkl")
    print(f"✓ Best model: {best_name}")
    print(f"✓ Accuracy: {best_accuracy:.3f}")
    
    # Show final evaluation
    y_pred = best_model.predict(X_test)
    print("\n=== FINAL EVALUATION ===")
    print(classification_report(y_test, y_pred))
    
    return best_model, tfidf

if __name__ == "__main__":
    train_new_model()