# Augusta PM Agent

An AI-powered **Project Management Agent** for Augusta's client engagements. Events trigger the agent, which reasons using persistent memory and automatically generates emails, proposals, team plans, and meeting briefings.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Single-Server App                     │
│                                                         │
│  FastAPI (port 8000)                                    │
│  ├── /              → Serves HTML UI (React in-browser) │
│  ├── /api/events/*  → Agent event endpoints             │
│  ├── /api/clients/* → Client & memory endpoints         │
│  └── /api/chat      → Chat interface                    │
│                                                         │
│  Agent System                                           │
│  ├── orchestrator.py  → Routing + branching logic       │
│  ├── skills.py        → Modular prompt-based tools      │
│  └── llm.py           → OpenAI client wrapper           │
│                                                         │
│  Memory                                                 │
│  └── store.py         → JSON file persistence           │
└─────────────────────────────────────────────────────────┘
```

---

## Features

### 3 Event Triggers
| Button | What it does |
|---|---|
| **Meeting Transcript came in** | Extracts insights → always drafts follow-up email → optionally generates proposal + internal team plan based on content |
| **Email Reply came in** | Reads full project context → drafts a contextual, comprehensive reply |
| **Meeting in 3 hours** | **New client?** → Research report (company overview, business model, attendees, suggested questions). **Existing client?** → Meeting prep briefing (status, open items, risks, suggested agenda) |

### Agent Outputs
- 📧 **Follow-up emails** — specific, referencing actual meeting details
- 📄 **Proposals** — structured Markdown with scope, timeline, investment
- ✅ **Internal team plans** — action items table, risks, client relationship notes
- 🧠 **Pre-meeting briefings** — status snapshot, open items, talking points
- 🔍 **Research reports** — company overview, industry context, suggested questions

### Memory System
- Persists project state across events (JSON file)
- Tracks: events log, open items, decisions, project status, client sentiment
- Memory evolves as you run events in sequence — later outputs reference earlier context
- Visual memory panel in UI shows current state

### Chat Interface
- Ask questions about any engagement
- Suggested prompts: open items, risks, project status, meeting prep
- Full project context injected into every message

---

## Test Data

Two pre-loaded clients, each with a realistic multi-meeting engagement:

### FinoVa Capital (Fintech)
Real-time data pipeline modernisation for a mid-market investment fund. $315k engagement, Q3 deadline, Meridian Fund at risk.
- **T1** — Kickoff: discovery, 18-hour lag problem, ballpark $280-320k
- **T2** — Technical Deep-Dive: Kafka + Snowflake architecture, 12-week plan
- **T3** — SOW Negotiation: $290k agreed, 35/35/30 payment, July 25 go-live
- **Email** — James Liu: rate limits on broker APIs, security review request

### MedBridge Health (Healthcare)
Predictive readmission platform for 2.3M patient records across 47 clinic partners. Series B funded, grant deadline August 31.
- **T1** — Discovery: HIPAA compliance, EMR fragmentation, $400k budget
- **T2** — Architecture Workshop: Azure + FHIR + Databricks design, Presidio for de-id
- **T3** — Kickoff sign-off: $360k ceiling, August 15 milestone, BAA finalised
- **Email** — Nina Patel: Azure access, 3 clinics mid-EMR-migration, Presidio concerns

### Suggested Demo Flow
1. Select **FinoVa** → click **Meeting in 3 hours** → see Research Report (no memory yet)
2. Click **Transcript** (T1 Kickoff) → see Email + Proposal + Team Plan + memory builds
3. Click **Transcript** (T2) → outputs now reference T1 context
4. Click **Transcript** (T3) → full history in every output
5. Click **Meeting in 3 hours** again → now see Meeting Prep (not research)
6. Click **Email Reply came in** → context-aware reply to James Liu's concerns
7. Open **Chat** → ask "What are the biggest risks?" or "What should I prep for Monday?"

---

## Running Locally

### Prerequisites
- Python 3.10+
- An OpenAI-compatible API key (set `OPENAI_API_KEY` or `GSK_TOKEN`)

### Setup

```bash
git clone <repo-url>
cd webapp

# Install Python dependencies
pip install fastapi uvicorn openai pydantic python-dotenv aiofiles python-multipart

# Set your API key
export OPENAI_API_KEY=your-key-here
# or
export GSK_TOKEN=your-genspark-token

# Start the server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

### Environment Variables
| Variable | Description |
|---|---|
| `GSK_TOKEN` | GenSpark token (checked first) |
| `OPENAI_API_KEY` or `GENSPARK_TOKEN` | Alternative API keys |
| `OPENAI_BASE_URL` | API base URL (default: GenSpark proxy) |

The app also auto-reads `~/.genspark_llm.yaml` if present.

---

## Project Structure

```
webapp/
├── backend/
│   ├── main.py              # FastAPI app — all routes + static UI serving
│   ├── agent/
│   │   ├── llm.py           # OpenAI client wrapper (auth, model selection)
│   │   ├── skills.py        # Modular prompt tools (7 skills)
│   │   └── orchestrator.py  # Event routing + branching logic
│   ├── memory/
│   │   └── store.py         # JSON persistence (read/write client state)
│   ├── data/
│   │   └── test_data.py     # 2 clients × 3 transcripts + 1 email each
│   └── static/
│       └── index.html       # Full React SPA (inline, no build step)
└── README.md
```

---

## Agent Skills

| Skill | Trigger | Output |
|---|---|---|
| `extract_transcript_insights` | Every transcript | Structured JSON: decisions, action items, risks, sentiment |
| `draft_followup_email` | Every transcript | Client-facing follow-up email |
| `generate_proposal` | When commitments detected | Scoped proposal in Markdown |
| `generate_team_plan` | When tasks detected | Internal action table with owners |
| `generate_research_report` | Meeting, no prior memory | Company + industry research |
| `generate_meeting_prep` | Meeting, existing memory | Status, open items, agenda, talking points |
| `draft_email_reply` | Email event | Full contextual reply addressing every point |

---

## Design Decisions

- **Single server** — FastAPI serves both the API and the React UI (no separate frontend build/deploy)
- **In-browser React** — Babel + CDN React, no webpack/bundler required; instant startup
- **JSON memory** — Simple flat file (`memory/memory.json`), easy to inspect and debug
- **Reasoning model** — Uses `gpt-4o-mini` with raised `max_tokens` to account for chain-of-thought overhead
- **Modular skills** — Each output type is a separate function; easy to add new skills or swap prompts
- **Branching logic** — Meeting handler checks memory presence; transcript handler checks insight flags for optional outputs
