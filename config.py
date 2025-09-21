import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_news_api_key_here')
GOOGLE_FACT_CHECK_API_KEY = os.getenv('GOOGLE_FACT_CHECK_API_KEY', 'your_google_fact_check_key')

# Configuration
class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Choose the appropriate config
config = DevelopmentConfig