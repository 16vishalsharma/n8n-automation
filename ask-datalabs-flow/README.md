# Ask DataLabs Flow - n8n Workflow

## Overview
This is the **AskInc42 | Prod | Main** n8n workflow converted to local usage. It's a complex LangChain-based chat system with advanced features like caching, multi-source data retrieval, and deep research modes.

## Folder Structure
```
ask-datalabs-flow/
├── main.json                 # The main n8n workflow
├── README.md                 # This file
├── NODES.md                  # Detailed node breakdown
└── SETUP.md                  # Setup & import instructions
```

## Quick Import Steps

### 1. **Local n8n Setup**
Ensure you have n8n running locally:
```bash
docker run -it -p 5678:5678 n8nio/n8n
# OR via npm:
npx n8n start
```

### 2. **Import the Flow**
- Go to `http://localhost:5678`
- Click **"New" → "Open from file"**
- Select: `/Users/cepl/Documents/n8n-automation/ask-datalabs-flow/main.json`
- Click **Import** and confirm

### 3. **Configure Credentials**
The workflow requires several credential types:
- **OpenAI** (for ChatGPT, embeddings, etc.)
- **Pinecone** (vector DB, if used)
- **Tavily** (for web search, if used)
- **Redis** (for caching, optional)
- **MongoDB** (for data storage, if used)

Add these under **Settings → Credentials** before running.

### 4. **Activate Workflows**
- After import, click **Active** toggle to enable the webhooks
- Note the webhook URLs for integration

## Main Nodes

| Node | Type | Purpose |
|------|------|---------|
| When chat message received | Chat Trigger | Entry point for chat UI |
| Webhook | Webhook | HTTP POST endpoint for `/ask` |
| OPT-004: Check Cache | Code | Cache lookup (Redis + static storage) |
| [Many others...] | Various | Processing, AI, data retrieval |

## Key Features

✅ **Streaming Chat Response**  
✅ **Multi-Mode Support** (fast, thinking, deep_research)  
✅ **Cache Optimization** (Redis + static storage)  
✅ **Recursive Call Guard** (EDGE-11)  
✅ **Security Hardening** (SEC-07 normalization)  
✅ **Web Search Integration**  
✅ **Vector DB Support** (Pinecone)  

## Files in Folder

- **main.json** - Complete workflow JSON export
- **NODES.md** - Breakdown of all 40+ nodes and their functions
- **SETUP.md** - Detailed setup & configuration guide

## Next Steps

1. ✅ Copy flow to local folder: **Done**
2. → Import into local n8n
3. → Configure all credentials
4. → Test webhook at `/ask` endpoint
5. → Deploy to production

---

**Last Updated:** 6 April 2026  
**Workflow Name:** AskInc42 | Prod | Main  
**Status:** Ready for import & deployment
