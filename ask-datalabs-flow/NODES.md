# AskInc42 Flow - All Nodes

**Total Nodes:** 69

## Node List

| # | Node Name | Type |
|---|-----------|------|
| 1 | When chat message received | langchain.chatTrigger |
| 2 | Webhook | webhook |
| 3 | OPT-004: Check Cache | code |
| 4 | OPT-004: Route Cache | switch |
| 5 | OPT-004: Format Cached Response | code |
| 6 | Classify Query Type | code |
| 7 | Decomposer: Route | if |
| 8 | Decomposer: Parse Response | code |
| 9 | Decomposer | langchain.openAi |
| 10 | Split Out | splitOut |
| 11 | Loop Over Items | splitInBatches |
| 12 | Aggregate | aggregate |
| 13 | Code in JavaScript | code |
| 14 | Switch | switch |
| 15 | Switch1 | switch |
| 16 | AskInc42 Agent | langchain.agent |
| 17 | Respond to Webhook (latest version)1 | respondToWebhook |
| 18 | Inc42 Updates1 | langchain.toolWorkflow |
| 19 | Inc42 Context1 | langchain.toolWorkflow |
| 20 | OpenAI Chat Model1 | langchain.lmChatOpenAi |
| 21 | Datalabs1 | langchain.toolWorkflow |
| 22 | Merge | merge |
| 23 | Respond to Webhook (latest version) | respondToWebhook |
| 24 | OPT-016 Phase 1: Parse Criteria | code |
| 25 | OPT-029: Detect Tool Bypass | code |
| 26 | OPT-017: Route Based on Bypass | switch |
| 27 | OPT-017: Add Max Retry Warning | code |
| 28 | OPT-024: Enforce Source Citations | code |
| 29 | OPT-031: Aggregation Post-Processing | code |
| 30 | Format Response | code |
| 31 | OPT-004: Write Cache | code |
| 32 | OPT-017: Retry with Tool Guidance | langchain.agent |
| 33 | OPT-083: Honest Response Formatter | code |
| 34 | OPT-094: Clean Response | code |
| 35 | OPT-079: Timeout Budget | code |
| 36 | OPT-111: Simple Query Fast-Path | code |
| 37 | OPT-111: Route Fast-Path | switch |
| 38 | OPT-122: Source Sufficiency Check | code |
| 39 | OPT-122: Route Augmentation | switch |
| 40 | OPT-123: Prepare Sonar Request | code |
| 41 | OPT-123: Perplexity Sonar | httpRequest |
| 42 | OPT-124: Merge Augmented Sources | code |
| 43 | OPT-147: Coherence Post-Processor | code |
| 44 | OPT-151: Auth Check | code |
| 45 | OPT-155a: Read Session | code |
| 46 | OPT-155b: Write Session | code |
| 47 | OPT-048: Query Suggestions | code |
| 48 | Shared Prompt Config | code |
| 49 | Route: NDJSON? | if |
| 50 | Respond NDJSON | respondToWebhook |
| 51 | Route: NDJSON Cached? | if |
| 52 | Respond NDJSON Cached | respondToWebhook |
| 53 | ScoutDB | langchain.toolWorkflow |
| 54 | OPT-D: Ultra-Fast Classifier | code |
| 55 | OPT-D: Direct ES Query | code |
| 56 | OPT-D: Route ES Result | if |
| 57 | OPT-D: Format Direct Response | code |
| 58 | SEC-01: Input Validation | code |
| 59 | SEC-01: Rejection Router | if |
| 60 | SEC-01: Respond Rejected | respondToWebhook |
| 61 | EDGE-01: Sub-Workflow Health Check | code |
| 62 | SEC-06: Auth Router | if |
| 63 | SEC-06: Respond Unauthorized | respondToWebhook |
| 64 | OPT-155c: Query Resolver | code |
| 65 | Parallel Fetch | code |
| 66 | Route: Skip Decomposer? | if |
| 67 | Datalabs | executeWorkflow |
| 68 | Inc42 Hybrid Rag Live | executeWorkflow |
| 69 | env | code |
