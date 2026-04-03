# News Scraping Code (LangChain)

This folder contains a Python implementation that mirrors your n8n workflow in code:

- Schedule trigger (via cron / script run)
- Topic normalization and default categories
- NewsAPI fetch + Google News RSS fetch
- Article deduplication
- OpenAI classification and summary with streaming token output
- MongoDB upsert storage

## Setup

1. `cd news-scraping-code`
2. `pip install -r requirements.txt`
3. create `.env`:

```
NEWSAPI_KEY=your_newsapi_key
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=mongodb://localhost:27017
MONGO_DB=newsdb
```

## Run

- Single topic: `python news_scraper.py --topic "gold price news"`
- All default topics: `python news_scraper.py --auto`

## Streaming

This uses `langchain.chat_models.ChatOpenAI` with `streaming=True` plus `StreamingStdOutCallbackHandler` to print tokens as they arrive, similar to n8n streaming intent.

## Notes

- For the n8n "Scrape Article Page" optional node, add a dedicated `requests` + `BeautifulSoup` function if needed.
- You can swap `ChatOpenAI` to `OpenAI` in LangChain to support `langgraph` later (or integrate with actual `langgraph` SDK).