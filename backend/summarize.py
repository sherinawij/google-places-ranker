import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
def summarize_place(place):
    reviews = place.get("reviews", [])
    if not reviews:
        return "No reviews available."
    review_texts=""
    for review in reviews:
        text = review["text"]["text"]
        review_texts += text
    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "user", "content": f"Summarize the following customer reviews in one sentence: <reviews>{review_texts}</reviews>"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        # print(e)
        return "Summary temporarily unavailable."