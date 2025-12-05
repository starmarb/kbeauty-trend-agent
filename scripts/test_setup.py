"""Test that everything is set up correctly."""
import sys

def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    try:
        import anthropic
        import praw
        import sqlalchemy
        import redis
        import pandas
        import langdetect
        from config.settings import settings
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_database():
    """Test database connection."""
    print("\nTesting database connection...")
    try:
        from src.db import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_redis():
    """Test Redis connection."""
    print("\nTesting Redis connection...")
    try:
        import redis
        from config.settings import settings
        
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


def test_anthropic():
    """Test Anthropic API key."""
    print("\nTesting Anthropic API...")
    try:
        from config.settings import settings
        
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your-api-key-here":
            print("⚠️  Anthropic API key not set (add later)")
            return True
        
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        print("✅ Anthropic client initialized")
        return True
    except Exception as e:
        print(f"❌ Anthropic setup failed: {e}")
        return False


def test_reddit():
    """Test Reddit API credentials."""
    print("\nTesting Reddit API...")
    try:
        from config.settings import settings
        
        if not settings.REDDIT_CLIENT_ID or settings.REDDIT_CLIENT_ID == "your-client-id":
            print("⚠️  Reddit credentials not set (add later)")
            return True
        
        import praw
        reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT
        )
        subreddit = reddit.subreddit("AsianBeauty")
        _ = subreddit.display_name
        print("✅ Reddit API connection successful")
        return True
    except Exception as e:
        print(f"❌ Reddit API failed: {e}")
        return False


def test_tables():
    """Test that database tables exist."""
    print("\nTesting database tables...")
    try:
        from src.db import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            count = result.scalar()
            if count >= 8:
                print(f"✅ Database has {count} tables")
                return True
            else:
                print(f"❌ Expected 8 tables, found {count}")
                return False
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("K-Beauty Trend Agent - Setup Verification")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Redis", test_redis()))
    results.append(("Tables", test_tables()))
    results.append(("Anthropic", test_anthropic()))
    results.append(("Reddit", test_reddit()))
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! Ready for Phase 1.")
    else:
        print("⚠️  Some tests failed. Please fix before proceeding.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
