import os
import json
import re
from typing import Any, Dict, List

import httpx
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pymongo import MongoClient

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "notify_db")

if not OPENAI_API_KEY:
    raise SystemExit("OPENAI_API_KEY is required")

openai.api_key = OPENAI_API_KEY

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
news_collection = db.news
latest_news_collection = db.latest_news

app = FastAPI(title="ask-new API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now; restrict to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def get_db_context(query: str, max_items: int = 5) -> List[Dict[str, Any]]:
    # Text search on title + description (if text index exists). Fallback to regex.
    q = normalize_text(query)
    items = []

    if q:
        try:
            items = list(news_collection.find({"$text": {"$search": q}}, {"score": {"$meta": "textScore"}}).sort([("score", {"$meta": "textScore"})]).limit(max_items))
        except Exception:
            items = list(news_collection.find({"$or": [{"title": {"$regex": q, "$options": "i"}}, {"description": {"$regex": q, "$options": "i"}}]}).limit(max_items))

    return [
        {
            "title": normalize_text(item.get("title", "")),
            "description": normalize_text(item.get("description", "")),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
        }
        for item in items
    ]


def get_internet_context(query: str, max_items: int = 5) -> List[Dict[str, Any]]:
    url = "https://newsapi.org/v2/everything"
    headers = {"Authorization": NEWSAPI_KEY} if NEWSAPI_KEY else {}
    params = {"q": query, "language": "en", "pageSize": max_items, "sortBy": "relevancy"}

    if not NEWSAPI_KEY:
        return []

    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []

    data = resp.json()
    articles = data.get("articles", [])

    return [
        {
            "title": normalize_text(item.get("title", "")),
            "description": normalize_text(item.get("description", "")),
            "source": item.get("source", {}).get("name", ""),
            "url": item.get("url", ""),
        }
        for item in articles
    ]


def build_prompt(query: str, db_context: List[Dict[str, Any]], internet_context: List[Dict[str, Any]]) -> str:
    db_text = "\n".join([f"- {i+1}. {item['title']} ({item['source']}): {item['description']}" for i,item in enumerate(db_context)])
    web_text = "\n".join([f"- {i+1}. {item['title']} ({item['source']}): {item['description']}" for i,item in enumerate(internet_context)])

    return (
        "You are a research assistant. Answer the user query using the provided database and internet context. "
        "If the query is not covered, say so and still provide the best helpful answer. Then rewrite the answer clearly and concisely. "
        "Return plain text only."
        "\n\nUser query: " + query + "\n\n"
        "Database context:\n" + (db_text or "None") + "\n\n"
        "Internet context:\n" + (web_text or "None") + "\n\n"
        "Final response:"
    )


@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    query = normalize_text(body.get("query", ""))
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    db_data = get_db_context(query, max_items=5)
    internet_data = get_internet_context(query, max_items=5)

    prompt = build_prompt(query, db_data, internet_data)
    print("Generated prompt", prompt)
    async def generate():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                stream=True
            )
            print("Streaming response started", response)
            for chunk in response:
                delta = chunk['choices'][0].get('delta', {})
                content = delta.get('content', '')
                if content:
                    yield f"data: {json.dumps({'chunk': content})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/status")
async def status():
    return {"status": "ok", "db_count": news_collection.count_documents({}), "latest_count": latest_news_collection.count_documents({})}


# Example run command:
# uvicorn ask_new:app --host 0.0.0.0 --port 8001

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
