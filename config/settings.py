import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/kbeauty_trends"
    )
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Reddit
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "KBeautyTrendAgent/1.0")
    
    # YouTube
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
    # Collection settings
    TARGET_SUBREDDITS = [
        "AsianBeauty",
        "SkincareAddiction",
        "KoreanBeauty",
    ]
    
    # Analysis settings
    AUTHENTICITY_THRESHOLD = 0.6
    TREND_VOLUME_THRESHOLD = 500  # mentions per week
    TREND_VELOCITY_THRESHOLD = 1.0  # 100% week-over-week growth


settings = Settings()