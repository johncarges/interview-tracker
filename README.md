# Interview Tracker

A local-first job search tracker designed to be used natively with Claude Code. Instead of a
web UI, you describe what you want in natural language and Claude either runs a convenience
script or writes a short Python snippet against the local SQLite database.

---

## How It Works

There are two interaction modes:

**Convenience scripts** handle mutations and common queries — operations with side effects,
validation, or frequent enough to be worth a dedicated command:

```bash
uv run python scripts/add_company.py "Stripe" --industry fintech
uv run python scripts/pipeline_summary.py
uv run python scripts/upcoming_interviews.py
```

**Ad-hoc Python** handles everything else. For flexible or one-off questions, Claude writes
a short snippet directly against the service and repository layer — no new script required:

> *"Show me edtech companies I've saved but haven't applied to yet"*
> *"Which of my active applications haven't had any interviews scheduled?"*
> *"List all roles mentioning React that I applied to in the last 30 days"*

`CLAUDE.md` is the operating manual for this interaction model — it's committed to the repo
intentionally as part of the app, not personal config.

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

The app has two intentionally simple components:

- **Client**: Claude Code — runs scripts or writes ad-hoc Python directly
- **Storage**: SQLite, a single local file configured via `DATABASE_URL` in `.env`

Both are designed to be swapped out independently as needs grow:

- **Scaling storage**: change `DATABASE_URL` to a Postgres connection string — nothing else changes
- **Scaling the client**: the service layer is already decoupled from the CLI, so adding a
  FastAPI layer means writing route handlers that call the same services used today
