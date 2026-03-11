# Sales Context Agent

Pre-meeting briefs powered by [Airweave](https://airweave.ai). Pulls context from your CRM, docs, and codebase so you walk into every call prepared.

## Why This Exists

Sales reps waste time scrambling for context before calls. The information exists, scattered across Notion pages, Google Drive docs, and GitHub repos, but finding it takes too long.

This agent uses Airweave to search across all your connected sources at once and synthesize the results into a structured pre-meeting brief.

## What It Does

```
Briefing Request --> [Decomposition] --> [Source Search] --> [Synthesis] --> Account Brief
                          |                   |                  |
                          +-- Breaks into     +-- Airweave       +-- LLM synthesizes
                              targeted            searches           into structured
                              queries             Notion, Drive,     brief with
                              per source          GitHub             talking points
```

*Example: "Prep me for the Acme Analytics call" --> 6 targeted queries --> 8 relevant docs --> structured brief with 5 sections*

---

# Part 1: Interactive Demo

The frontend provides a visual walkthrough of the pipeline. It works out of the box with sample data -- no API keys needed.

## Quick Start (2 minutes)

```bash
# Clone and setup
git clone https://github.com/airweave-ai/sales-context-agent.git
cd sales-context-agent
cp .env.example .env

# Optional: Add LLM key for smarter query decomposition (works without it too)
# ANTHROPIC_API_KEY=your_key  (or OPENAI_API_KEY)

# Start backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and click **Generate Brief**.

## What the Demo Shows

The interactive visualization walks you through:

1. **Briefing Request** - Account name, meeting topic, and attendees
2. **Query Decomposition** - Request broken into targeted queries tagged by source (Notion, Google Drive, GitHub)
3. **Source Search** - Results from each source with relevance scores, found via Airweave
4. **Context Synthesis** - Search results combined into a structured brief with 5 sections
5. **Brief Output** - Full rendered brief with copy-to-clipboard and optional Slack posting

The demo uses:
- **Sample data** by default (realistic brief for "Acme Analytics" at PostHog)
- **Mock search results** showing what Airweave would return
- **Preview mode** for Slack (no actual messages sent)

---

# Part 2: Production Setup

To use this for real pre-meeting prep:

## Step 1: Connect Airweave for Cross-Source Search

This is the core of the agent -- Airweave searches your Notion, Google Drive, GitHub, and 50+ other sources.

```bash
AIRWEAVE_API_KEY=your_key
AIRWEAVE_COLLECTION_ID=your_collection
AIRWEAVE_API_URL=https://api.airweave.ai  # or self-hosted
```

**Set up your Airweave collection:**
1. Create a collection at [airweave.ai](https://airweave.ai)
2. Connect your sources (Notion, Google Drive, GitHub, Slack, etc.)
3. Wait for initial sync to complete

Now the agent will search your actual docs and repos when generating briefs.

## Step 2: Add an LLM Provider

Used for query decomposition and brief synthesis.

```bash
# Option 1: Anthropic (recommended)
ANTHROPIC_API_KEY=your_key
# ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Option 2: OpenAI
OPENAI_API_KEY=your_key
# OPENAI_MODEL=gpt-4o
```

## Step 3: Enable Slack (Optional)

Post generated briefs directly to a Slack channel.

```bash
SLACK_ENABLED=true
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL_ID=C0123456789
```

## Step 4: Run

### As an API Service

```bash
uvicorn main:app --host 0.0.0.0 --port 8000

# Trigger a brief via API
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"use_sample_data": false, "briefing_request": {"account": "Acme Corp", "topic": "Q1 renewal", "attendees": ["Jane Smith"]}}'
```

### Programmatically

```python
import asyncio
from main import run_pipeline, PipelineConfig

async def main():
    config = PipelineConfig(
        use_sample_data=False,
        briefing_request={
            "account": "Acme Corp",
            "topic": "Q1 renewal discussion",
            "attendees": ["Jane Smith", "Bob Johnson"],
        },
        post_to_slack=True,
    )
    result = await run_pipeline(config)
    print(f"Pipeline completed: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

# How It Works

## Pipeline Stages

| Stage | What It Does | How |
|-------|-------------|-----|
| Briefing Request | Captures account, topic, attendees | User input or API call |
| Decomposition | Breaks request into 4-6 targeted queries | LLM with source tagging (Notion, Drive, GitHub) |
| Source Search | Searches each query against the right source | Airweave SDK with `source_name` filtering |
| Synthesis | Combines results into structured brief | LLM produces 5 sections |
| Output | Renders brief, optionally posts to Slack | Markdown + Slack Block Kit |

## Brief Structure

Every generated brief includes:

- **Account Snapshot** - Company overview, tier, engagement history
- **Relationship History** - Past interactions, key contacts, deal context
- **Open Concerns** - Active issues, support tickets, blockers
- **Product Updates** - Recent changes relevant to this account
- **Talking Points** - Specific items to raise in the meeting

## Context Search via Airweave

The agent uses Airweave's source filtering to search the right tool for each query:

```python
from airweave import AirweaveSDK

client = AirweaveSDK(api_key=AIRWEAVE_API_KEY)

# Search Notion for account context
results = client.search.search(
    collection_id=COLLECTION_ID,
    query="Acme Analytics account overview",
    source_name="notion",
    limit=5
)

# Search GitHub for technical details
results = client.search.search(
    collection_id=COLLECTION_ID,
    query="Acme custom integration",
    source_name="github",
    limit=5
)
```

---

# Project Structure

```
├── backend/
│   ├── main.py              # FastAPI + WebSocket + Pipeline orchestration
│   ├── config.py            # Configuration management
│   ├── schemas.py           # Pydantic data models
│   ├── samples/             # Sample briefing data for demo
│   ├── clients/             # External APIs (Airweave, Slack)
│   └── pipeline/
│       ├── decomposition.py # Query decomposition with source tagging
│       ├── search.py        # Airweave cross-source search
│       ├── synthesis.py     # LLM-powered brief generation
│       └── output.py        # Brief output + Slack posting
├── frontend/                # React demo visualization
│   ├── src/
│   │   ├── App.tsx          # Main app with WebSocket connection
│   │   └── components/      # Pipeline visualization components
└── .env.example             # All available environment variables
```

---

# API Reference

## REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/config` | GET | Current configuration status |
| `/api/samples` | GET | Sample briefing data |
| `/api/run` | POST | Trigger pipeline run |

## WebSocket

Connect to `/ws/pipeline` for real-time pipeline updates (used by the frontend):

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/pipeline');
ws.send(JSON.stringify({ type: 'run', config: { use_sample_data: true } }));
ws.onmessage = (e) => {
  const event = JSON.parse(e.data);
  // Events: pipeline_started, step_started, step_data_ready, step_completed, pipeline_completed
};
```

---

# Configuration Reference

See [.env.example](.env.example) for all options. Key settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `AIRWEAVE_API_KEY` | Airweave API key for cross-source search | - |
| `AIRWEAVE_COLLECTION_ID` | Collection with connected sources | - |
| `ANTHROPIC_API_KEY` | Anthropic key for LLM decomposition/synthesis | - |
| `SLACK_ENABLED` | Enable posting briefs to Slack | `false` |

---

# Learn More

- [Airweave Documentation](https://docs.airweave.ai)
- [Airweave Python SDK](https://pypi.org/project/airweave/)

## License

MIT License - use this as a starting point for your own sales context agent.

---

Built with [Airweave](https://airweave.ai) - unified search across all your apps and databases.
