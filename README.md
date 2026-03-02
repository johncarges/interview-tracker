# Interview Tracker

A local-first job search tracker designed to be used natively with Claude Code. Instead of a web UI, you describe what you want in natural language and Claude runs the right script against a local SQLite database.

---

## How It Works

The primary interface is conversation. You tell Claude things like:

- *"Add a company: Acme Corp, they're a Series B edtech startup"*
- *"I applied to the Staff Engineer role at Stripe"*
- *"Schedule a technical interview for my Google application next Tuesday at 2pm"*
- *"What interviews do I have coming up this week?"*
- *"Give me a summary of my whole pipeline"*

Claude interprets the request, runs the appropriate script, and formats the results.

---

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/johncarges/interview-tracker
cd interview-tracker
uv sync --extra dev
cp .env.example .env
uv run python scripts/init_db.py
```

---

## Architecture

The app currently has two intentionally simple components:

- **Client**: Claude Code runs scripts in `scripts/` directly — no server, no frontend
- **Storage**: SQLite, a single local file configured via `DATABASE_URL` in `.env`

Both are designed to be swapped out independently as needs grow:

- **Scaling storage**: change `DATABASE_URL` to a Postgres connection string — nothing else in the codebase changes
- **Scaling the client**: the service layer is already decoupled from the CLI, so adding a FastAPI layer on top means writing route handlers that call the same services the scripts use today
