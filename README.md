# Augusta PM Agent

An AI-powered **Project Management Agent** for Augusta's client engagements. Events trigger the agent, which reasons using persistent memory and automatically generates emails, proposals, team plans, and meeting briefings.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Single-Server App                    │
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

### Atlassian (B2B SaaS)
AI-enabled product rebuild for a project/workflow management company under competitive pressure.
- **T1** - Intro Call: discovery, product rebuild goals, Q3 urgency
- **T2** - Scoping Call: architecture, customer flows, migration questions
- **T3** - Project Kickoff: implementation plan, owners, evaluation approach
- **Email** - Henrik Aalsbjerg: proposal follow-up and project concerns

### Marsh McLennan (Insurance / Risk Advisory)
Agentic workflow automation for broker operations and submission handling.
- **T1** - Intro Call: broker workflow discovery, Acturis constraints, Azure preference
- **T2** - Proposal Walkthrough: scope, pricing, IP ownership, security controls
- **T3** - Week 1 Status: blockers, named owners, checkpoint planning
- **Email** - Rebecca Halloway: revised proposal and implementation concerns

### Suggested Demo Flow
1. Select **Atlassian** → click **Meeting in 3 hours** → see Research Report (no memory yet)
2. Click **Run** on Call 1 → see generated follow-up email and memory builds
3. Leave the client and return → Call 1 now shows **Show** instead of **Run**
4. Click **Run** on Call 2 or Call 3 → outputs reference earlier project memory
5. Click **Meeting in 3 hours** again → now see Meeting Prep (not research)
6. Click **Email reply came in** → context-aware reply to Henrik's concerns
7. Open **Chat** → ask "What are the biggest risks?" or "What should I prep for Monday?"

---

## Running Locally

### Prerequisites
- Python 3.10+
- An OpenAI-compatible API key

### Setup

```bash
git clone <repo-url>
cd agentaugusta

# Install Python dependencies
python -m pip install -r backend/requirements.txt

# Create your local environment file
cp .env.example .env
```

On Windows `cmd.exe`, use:

```bat
copy .env.example .env
```

Open `.env` and set at least:

```env
OPENAI_API_KEY=sk-your-openai-key-here
```

Optional Langfuse tracing can also be enabled in `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Then start the server:

```bash
# Start the server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

On Windows, if `python` is not available, use `python3` in the commands above.

### Environment Variables
| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Required OpenAI API key |
| `OPENAI_BASE_URL` | Optional OpenAI-compatible API base URL |
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key for tracing |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key for tracing |
| `LANGFUSE_BASE_URL` | Langfuse host, for example `https://cloud.langfuse.com` or `https://us.cloud.langfuse.com` |
| `LANGFUSE_TRACING_ENABLED` | Set to `false` to disable Langfuse tracing without code changes |

Langfuse onboarding remains `Pending` until the running server receives at least one traced request. After setting the variables above, restart uvicorn and trigger a transcript, meeting, email, or chat action in the UI.

### Submission Notes

- Do not include a real `.env` file in the zip. It is ignored by git and should stay local.
- Runtime memory is written to `backend/memory/memory.json` and is ignored by git so the reviewer starts from a clean demo state.
- The app is intentionally single-server: no frontend build step is required.

---

## Project Structure

```
agentaugusta/
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
