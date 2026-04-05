import os
import json
import re
import time
from datetime import datetime, date, time as dt_time
from pathlib import Path

import requests
import openai
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env if present
# python3 news_scraper.py --auto
# curl -X POST -N http://localhost:8002/ask -H "Content-Type: application/json" -d '{"query":"latest news on AI"}'
load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "notify_db")

if not NEWSAPI_KEY:
    raise SystemExit("Missing NEWSAPI_KEY in environment")
if not OPENAI_API_KEY:
    raise SystemExit("Missing OPENAI_API_KEY in environment")

openai.api_key = OPENAI_API_KEY

DEFAULT_TOPICS = [
    "latest breaking news today",
    "gold price news",
    "silver price commodity",
    "stock market price",
    "trending stocks india",
    "nifty sensex bse nse",
    "cryptocurrency bitcoin ethereum",
]

CATEGORY_KEYWORDS = {
    "Gold": ["gold", "commodity", "metal"],
    "Stocks": ["stock", "share", "market"],
    "Market": ["market", "economy", "indices"],
    "Technology": ["tech", "technology", "software", "ai", "cloud"],
    "Politics": ["politic", "government", "election"],
    "Economy": ["econom", "inflation", "gdp", "money"],
    "Cryptocurrency": ["crypto", "bitcoin", "ethereum", "token"],
    "Sports": ["sport", "cricket", "football", "tennis"],
    "Entertainment": ["movie", "music", "celebrity"],
    "Health": ["health", "covid", "medicine", "wellness"],
    "Science": ["science", "research", "space"],
}

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
news_collection = db.news
latest_news_collection = db.latest_news


def normalize_topic(raw_topic: str) -> str:
    return (raw_topic or "latest news").strip().lower()


def fetch_newsapi(topic: str, page_size: int = 10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "language": "en",
    }
    headers = {"x-api-key": NEWSAPI_KEY}
    resp = requests.get(url, params=params, headers=headers, timeout=25)
    resp.raise_for_status()
    data = resp.json()
    return data.get("articles", [])


def build_google_news_rss_url(topic: str) -> str:
    term = requests.utils.quote(topic)
    return f"https://news.google.com/rss/search?q={term}&hl=en-IN&gl=IN&ceid=IN:en"


def parse_google_rss(rss_text: str):
    from xml.etree import ElementTree as ET

    try:
        root = ET.fromstring(rss_text)
    except ET.ParseError:
        return []

    output = []
    for item in root.findall(".//item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        pub_date = item.findtext("pubDate", default="").strip()
        desc = item.findtext("description", default="").strip()

        try:
            pub_iso = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").isoformat()
        except Exception:
            pub_iso = datetime.utcnow().isoformat()

        output.append(
            {
                "title": title,
                "description": desc,
                "content": desc,
                "source": "Google News RSS",
                "url": link,
                "publishedAt": pub_iso,
                "scrapedFrom": "google-news-rss",
            }
        )
    return output


def fetch_google_rss_articles(topic: str):
    url = build_google_news_rss_url(topic)
    resp = requests.get(url, timeout=25)
    resp.raise_for_status()
    return parse_google_rss(resp.text)


def deduplicate_articles(articles):
    seen = set()
    deduped = []
    for a in articles:
        key = (a.get("title", "").strip().lower(), a.get("url", "").strip())
        if not key[0] or key in seen:
            continue
        seen.add(key)
        deduped.append(a)
    return deduped


def infer_category_from_text(text: str):
    text_lower = (text or "").lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return category
    return "Other"


def infer_topic_from_text(text: str):
    text_lower = (text or "").lower()
    if "gold" in text_lower:
        return "gold"
    if "silver" in text_lower:
        return "silver"
    if "crypto" in text_lower or "bitcoin" in text_lower or "ethereum" in text_lower:
        return "cryptocurrency"
    if "stock" in text_lower or "nifty" in text_lower or "sensex" in text_lower:
        return "stocks"
    if "market" in text_lower or "econom" in text_lower:
        return "market"
    return "other"


def openai_classify_and_summarize(article):
    prompt = (
        "You are a news analysis AI. Analyze the article and return ONLY valid JSON without markdown or extra text. "
        "Input is title and description. Output format: {topic, category, tags, summary}."
    )

    messages = [
        {"role": "system", "content": "You are a news analysis AI. Analyze articles and return ONLY valid JSON with no extra text or markdown."},
        {"role": "user", "content": f"Title: {article.get('title', '')[:800]}\nDescription: {article.get('description', '')[:1200]}"},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1,
        max_tokens=500,
    )

    text = response.choices[0].message.content.strip()

    # attempt to parse JSON from output
    cleaned = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()
    try:
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {
            "topic": "unknown",
            "category": "Other",
            "tags": [],
            "summary": article.get("description", "")[:400],
        }

    parsed["tags"] = ", ".join(parsed.get("tags", [])) if isinstance(parsed.get("tags"), list) else str(parsed.get("tags", ""))
    if parsed.get("topic", "unknown") in ["unknown", "", None]:
        parsed["topic"] = infer_topic_from_text(article.get("title", "") + " " + article.get("description", ""))
    if parsed.get("category", "Other") in ["Other", "other", "", None]:
        parsed["category"] = infer_category_from_text(article.get("title", "") + " " + article.get("description", ""))
    return parsed


def upsert_article(doc):
    query = {"title": doc.get("title")}
    update = {"$set": doc}
    news_collection.update_one(query, update, upsert=True)
    latest_news_collection.update_one(query, update, upsert=True)


def run(topic: str = None, force: bool = False):
    topic = normalize_topic(topic or "latest breaking news today")

    # Check daily limit
    today = date.today()
    start = datetime.combine(today, dt_time.min)
    end = datetime.combine(today, dt_time.max)
    count_today = news_collection.count_documents({"createdAt": {"$gte": start, "$lt": end}})
    if count_today >= 50 and not force:
        print(f"Daily limit of 50 articles reached ({count_today} already stored today). Skipping.")
        return

    # 1) ingest sources
    newsapi_articles = fetch_newsapi(topic)
    rss_articles = fetch_google_rss_articles(topic)

    all_raw = []
    for n in newsapi_articles:
        all_raw.append({
            "title": n.get("title", "").strip(),
            "description": n.get("description", ""),
            "content": n.get("content", ""),
            "source": n.get("source", {}).get("name", "newsapi"),
            "author": n.get("author", "Unknown"),
            "url": n.get("url", ""),
            "publishedAt": n.get("publishedAt", datetime.utcnow().isoformat()),
            "scrapedFrom": "newsapi",
        })
    for r in rss_articles:
        all_raw.append(r)

    deduped = deduplicate_articles(all_raw)

    # Limit to remaining slots (unless forced)
    if not force:
        max_to_process = 50 - count_today
        if max_to_process <= 0:
            print("No more articles to process today.")
            return
        deduped = deduped[:max_to_process]

    stored_docs = []

    # 2) classify and store
    for i, article in enumerate(deduped, start=1):
        print(f"\n=== Article {i}/{len(deduped)}: {article.get('title', '')[:80]} ===")
        ai = openai_classify_and_summarize(article)

        doc = {
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "content": article.get("content", ""),
            "source": article.get("source", ""),
            "author": article.get("author", "Unknown"),
            "url": article.get("url", ""),
            "publishedAt": article.get("publishedAt", ""),
            "topic": ai.get("topic", "unknown") or topic,
            "category": ai.get("category", "Other"),
            "tags": ai.get("tags", ""),
            "summary": ai.get("summary", ""),
            "scrapedFrom": article.get("scrapedFrom", ""),
            "createdAt": datetime.utcnow(),
            "searchTopic": topic,
        }

        upsert_article(doc)
        stored_docs.append(doc)

    print("\n✅ Completed run for topic:", topic)

    # Export latest run articles to JSON file
    out_path = Path("news-article.json").resolve()
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(stored_docs, f, ensure_ascii=False, indent=2)
    print("Wrote", len(stored_docs), "articles to", out_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="News scraper via NewsAPI + Google RSS with LangChain streaming classification")
    parser.add_argument("--topic", type=str, default=None, help="News topic to search")
    parser.add_argument("--auto", action="store_true", help="Run all default topics sequentially")
    parser.add_argument("--force", action="store_true", help="Ignore daily limit and force ingestion")
    args = parser.parse_args()

    if args.auto:
        for t in DEFAULT_TOPICS:
            run(t, force=args.force)
            time.sleep(2)
    else:
            run(args.topic, force=args.force)
