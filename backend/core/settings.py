from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    ENV = os.getenv("ENV", "development")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    FIREBASE_JSON = os.getenv("FIREBASE_JSON", "firebase.json")

settings = Settings()