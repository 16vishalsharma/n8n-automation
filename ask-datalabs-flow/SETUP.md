# Setup & Import Guide - AskInc42 Flow

## Prerequisites

1. **n8n Instance Running**
   ```bash
   # Option 1: Docker
   docker run -it -p 5678:5678 n8nio/n8n
   
   # Option 2: npm
   npx n8n start
   ```

2. **Access n8n UI**
   - Open: `http://localhost:5678`
   - Create an account if first time

## Step-by-Step Import

### Step 1: Access Import Dialog
1. Click the **"+"** icon (New Workflow)
2. Click **"Open from file"** at the top
3. Select: `/Users/cepl/Documents/n8n-automation/ask-datalabs-flow/main.json`

### Step 2: Confirm Import
- Review the workflow structure
- Click **"Import"** to load all nodes

### Step 3: Configure Credentials

The workflow requires these credential types (add them before activation):

#### OpenAI Credentials
- Type: **OpenAI**
- API Key: `sk-...`
- Models used: `gpt-4-turbo`, `gpt-4o`, `gpt-4o-mini`, `text-embedding-3-large`

#### Pinecone (Vector DB) - Optional
- Type: **Pinecone**
- API Key: Your Pinecone key
- Environment: `gd-1` (or your region)

#### Tavily Search - Optional
- Type: **HTTP Header Auth**
- Name: `Tavily API`
- API Key: Your Tavily key

#### Redis Cache - Optional
- Type: **Configuration**
- Host: `127.0.0.1`
- Port: `6379`
- Password: (if set)

#### MongoDB - Optional
- Type: **MongoDB**
- Connection String: `mongodb://localhost:27017`
- Database: `ask_datalabs`

### Step 4: Update Node Configurations

After importing, review and update these nodes:

1. **Webhook Node** - Verify path is `/ask`
2. **Chat Trigger** - Ensure responseMode is `streaming`
3. **HTTP Request Nodes** - Update API endpoints if needed
4. **Code Nodes** - Verify environment variables are accessible

### Step 5: Activate & Test

1. Toggle **"Active"** on the workflow
2. Wait for webhooks to register
3. Test via cURL:
   ```bash
   curl -X POST http://localhost:5678/webhook/ask \
     -H "Content-Type: application/json" \
     -d '{"chatInput": "What is AI?"}'
   ```

4. Or use the Chat UI at `http://localhost:5678/chat`

## Node Categories

### Trigger Nodes (Entry Points)
- `When chat message received` - LangChain Chat
- `Webhook` - HTTP POST endpoint

### Processing Nodes
- `OPT-004: Check Cache` - Cache lookup
- `OPT-009: Validate Input` - Input validation
- `Merge` - Data consolidation

### AI/LLM Nodes
- `ChatOpenAI` - LLM responses
- `Embeddings` - Vector embeddings
- `Tool Use` - Function calling

### Data Retrieval
- `HTTP Request` - API calls
- `Tavily Search` - Web search
- `Vector Store` - Pinecone queries
- `MongoDB` - Database queries

### Output Nodes
- `Response` - Send final answer back to client

## Troubleshooting

### Issue: "Credential not found"
**Solution:** Add missing credentials in Settings → Credentials before running

### Issue: "Webhook not registered"
**Solution:** Toggle workflow Active → Inactive → Active again

### Issue: "Timeout on first request"
**Solution:** Warm up the workflow by running a simple query first

### Issue: "Redis connection failed"
**Solution:** Redis is optional; workflow will use static storage as fallback

### Issue: "OpenAI API error"
**Solution:** Verify API key is correct and has sufficient quota

## Environment Variables

If using `.env` file, ensure these are set:

```bash
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
TAVILY_API_KEY=...
REDIS_PASSWORD=...
MONGO_URI=mongodb://localhost:27017
```

## Files in ask-datalabs-flow/

```
ask-datalabs-flow/
├── main.json           # Full workflow (69 nodes)
├── README.md          # Quick overview
├── SETUP.md           # This file
├── NODES.md           # Node breakdown
└── INTEGRATION.md     # API integration guide (optional)
```

## Next: Integration with Python API

After importing and testing:

1. **Update ask_new.py** to call n8n webhooks instead
2. **Replace direct OpenAI calls** with n8n workflow calls
3. **Route `/ask` requests** through n8n for advanced processing

Example integration:
```python
import httpx

async def ask_via_n8n(query: str):
    response = await httpx.post(
        "http://localhost:5678/webhook/ask",
        json={"chatInput": query}
    )
    return response.text
```

---

**Version:** 1.0  
**Last Updated:** 6 April 2026  
**Status:** Ready for Import
