# Onboarding Agent

> An AI-powered employee onboarding assistant that guides new hires through their first week — answering questions, tracking tasks, and notifying HR automatically.

---

## What it does

Most onboarding processes are a mess of spreadsheets, Slack pings, and forgotten tasks. This project replaces that with a conversational AI agent that:

- Detects who you are (role, experience, tech stack) from natural conversation
- Generates a personalized onboarding checklist on the fly
- Answers questions about company policies and setup guides using RAG over internal PDFs
- Tracks checklist completion in real-time through chat
- Fires a Slack welcome message the moment a new hire joins
- Sends a structured HR completion report via email when onboarding finishes
- Creates a GitHub starter issue assigned to the new hire
- Grows its own knowledge base by saving unanswered questions as FAQs

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| LLM | OpenRouter (Llama 3.1 via API) |
| Vector DB | ChromaDB (persistent, local) |
| RAG | PyMuPDF → chunked embeddings → similarity search |
| Database | SQLite |
| Notifications | Slack Incoming Webhooks |
| Email | SMTP (Gmail) |
| Version control | Git + GitHub |

---

## Architecture

```
User (React UI)
      │
      ▼
FastAPI /chat endpoint
      │
      ▼
ReAct Agent Loop ──────────────────────────────────────┐
      │                                                 │
      ├── tool: search_docs        → ChromaDB (RAG)     │
      ├── tool: mark_task_done     → SQLite             │
      ├── tool: get_checklist      → SQLite             │
      ├── tool: save_faq           → ChromaDB (write)   │
      └── tool: create_github_issue → GitHub API        │
                                                        │
On user creation  → Slack welcome message               │
On completion     → HR email + Slack report ◄───────────┘
```

The agent follows a **ReAct loop** — it reasons about what tool to call, calls it, observes the result, and continues until it has a final answer. This means it can chain multiple tool calls in a single turn (e.g. search docs → mark task → check if complete → send report).

---

## Features in depth

### Persona detection
The agent extracts name, role, experience level, and tech stack from the opening message without asking for structured input. A backend intern and a senior devops engineer get completely different checklists, generated at runtime from a role × experience matrix.

### RAG over internal docs
Three company PDFs (backend guide, frontend guide, HR policies) are chunked and embedded into ChromaDB on startup via `ingest.py`. When a user asks a setup question, the agent retrieves the top-k relevant chunks and grounds its answer in them — no hallucination about company-specific processes.

### Self-updating knowledge base
When the agent answers a question that wasn't in the original documents, it saves the Q&A pair back into ChromaDB as a FAQ entry. The knowledge base grows with every conversation — a core property of agentic systems.

### Real notifications
Slack messages and HR emails aren't mocked. They fire against real webhooks and SMTP. The HR completion email is a formatted HTML report with task breakdown, completion score, and timestamps.

---

## Project structure

```
onboarding-agent/
├── backend/
│   ├── main.py              # FastAPI app + ReAct agent loop
│   ├── agent_tools.py       # Tool definitions + implementations
│   ├── database.py          # SQLite schema + queries
│   ├── ingest.py            # PDF parsing + ChromaDB ingestion
│   ├── slack_helper.py      # Slack webhook functions
│   ├── email_helper.py      # SMTP HR report email
│   ├── create_docs.py       # Generates sample PDF documents
│   ├── documents/           # Source PDFs for RAG
│   ├── chroma_storage/      # Persisted vector embeddings
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx           # Root layout + theme toggle
    │   ├── App.css           # Design system + dark/light tokens
    │   └── components/
    │       ├── ChatWindow.jsx
    │       └── Checklist.jsx
    └── package.json
```

---

## Running locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Generate sample PDFs and ingest into ChromaDB
python create_docs.py
python ingest.py

# Start the API
uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI runs at `http://localhost:5173`.

### Environment variables

Create `backend/.env`:

```
OPENROUTER_API_KEY=
SLACK_WEBHOOK_GENERAL=
SLACK_WEBHOOK_HR=
SMTP_EMAIL=
SMTP_PASSWORD=
GITHUB_TOKEN=
GITHUB_REPO=
HR_EMAIL=
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a message, receive agent reply + updated checklist |
| `GET` | `/checklist/{user_id}` | Fetch a user's checklist and profile |
| `GET` | `/` | Health check |

### Chat request

```json
{
  "message": "Hi, I'm Priya. Backend intern, Node.js",
  "history": [],
  "user_id": null
}
```

### Chat response

```json
{
  "reply": "Welcome Priya! Here's your onboarding checklist...",
  "user_id": 1,
  "checklist": [
    { "id": 1, "task_name": "Install Node.js and npm", "is_completed": false },
    { "id": 2, "task_name": "Clone backend repository", "is_completed": false }
  ]
}
```

---

## Design decisions worth noting

**Why ReAct over a simple prompt?** A single LLM call can answer questions but can't update a database, fire a webhook, and check completion state in the same turn. The ReAct loop lets the agent take real actions with real side effects.

**Why ChromaDB over a hosted vector DB?** Zero infrastructure. The embeddings persist on disk and reload instantly. For a demo or internal tool, this is the right tradeoff.

**Why SQLite?** Onboarding is inherently sequential and low-volume. SQLite is zero-config and ships with Python. The schema is dead simple — users and checklists, linked by foreign key.

**Why two Slack webhooks?** Separation of concerns. `#general` gets a friendly welcome card visible to the whole team. `#hr-notifications` gets the structured completion report that HR actually needs to act on.

---

## What I'd improve with more time

- Auth layer — right now any user_id can query any checklist
- Stream the LLM response token by token instead of waiting for the full reply
- Replace polling with WebSockets for real-time checklist updates
- Add an admin dashboard to view all active onboardings
- Containerize with Docker for one-command setup
