# MapRank

Google Places search, re-ranked by rating and review count, with AI review summaries.

## Features

- Ranking that adjusts ratings for review volume
- AI review summaries (Groq)
- Sort, "open now" filter, and up to 60 results
- Accounts, favorites and personal notes
- Mobile-friendly

## Performance

- Search results are cached in Redis per page (15-minute TTL), so repeated searches skip the Google API.
- AI summaries are generated in parallel with a thread pool, cached per place in Redis, and loaded on demand for places outside the top 3.
- A first search takes about 1 s; a repeated search takes about 20 ms.
- Rate limiting per IP protects the search, summary and login routes.

## Getting started

### Prerequisites

- Python 3.10+
- Docker (to run Redis locally)
- A [Google Places API](https://developers.google.com/maps/documentation/places/web-service) key
- A [Groq](https://console.groq.com) API key

### Setup

```bash
git clone https://github.com/sherinawij/google-places-ranker.git
cd google-places-ranker

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GOOGLE_PLACES_API_KEY=your-google-key
GROQ_API_KEY=your-groq-key
SECRET_KEY=a-long-random-string
# optional:
# KV_URL=redis://localhost:6379
# DATABASE_URL=postgresql://...
```

Generate a `SECRET_KEY` with:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
### Run
```bash
docker run -d -p 6379:6379 redis:7
python backend/app.py
```

Open http://localhost:5000.

