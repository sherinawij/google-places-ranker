import os
import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("KV_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
