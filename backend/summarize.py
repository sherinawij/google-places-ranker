import os
from groq import Groq
from dotenv import load_dotenv
from cache import redis_client

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
# fail fast on rate limits instead of the SDK's silent retries
client = Groq(api_key=api_key, max_retries=0, timeout=10)
MAX_REVIEW_CHARS = 400
SUMMARY_TTL = 7 * 24 * 3600

def summarize_place(place):
    cache_key = f"summary:{place.get('id')}"
    cached_summary = redis_client.get(cache_key)
    if cached_summary is not None:
        return cached_summary
    reviews = place.get("reviews", [])
    if not reviews:
        return "No reviews available."
    review_texts=""
    for review in reviews:
        text = review.get("text", {}).get("text", "")
        if text:
            review_texts += text[:MAX_REVIEW_CHARS] + "\n"
    if not review_texts:
        return "No reviews available."
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "user", "content": f"Summarize the following customer reviews in one sentence under 20 words: <reviews>{review_texts}</reviews>"}
            ]
        )
        summary = response.choices[0].message.content
        redis_client.set(cache_key, summary, ex=SUMMARY_TTL)
        return summary
    except Exception as e:
        # print(e)
        return "Summary temporarily unavailable."