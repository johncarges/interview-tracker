# Interview Tracker — Claude's Operating Manual

## What This App Does

Local-first interview tracking. Data lives in a SQLite file at `data/interview_tracker.db`.
You interact by running scripts from the `scripts/` directory — no server required.
Claude acts as the UI: interpret natural language → run the right script → display results.

---

## One-Time Setup

```bash
uv sync --extra dev
cp .env.example .env          # already done if .env exists
uv run python scripts/init_db.py
```

---

## Natural Language → Script Mapping

| What the user says | Script to run |
|---|---|
| "Add a company: Acme Corp" | `scripts/add_company.py "Acme Corp"` |
| "Add a contact at Stripe" | `scripts/add_contact.py` |
| "Add a Staff Eng role at Google" | `scripts/add_role.py` |
| "I applied to the Stripe role" | `scripts/add_application.py` |
| "Schedule a phone screen for my Stripe app" | `scripts/add_interview.py` |
| "Update Stripe app status to interviewing" | `scripts/update_application.py` |
| "I passed the Stripe phone screen" | `scripts/complete_interview.py` |
| "What interviews do I have coming up?" | `scripts/upcoming_interviews.py` |
| "Who do I need to follow up with?" | `scripts/followup_contacts.py` |
| "What's the status of my Stripe application?" | `scripts/application_status.py` |
| "Give me my pipeline summary" | `scripts/pipeline_summary.py` |

---

## Script Reference

### Mutations
| Script | Key args |
|---|---|
| `init_db.py` | none |
| `add_company.py` | `NAME [--website] [--industry] [--notes]` |
| `add_contact.py` | `NAME --company-id INT [--title] [--email] [--phone] [--linkedin] [--notes]` |
| `add_role.py` | `TITLE --company-id INT [--url] [--salary-min] [--salary-max] [--notes]` |
| `add_application.py` | `--role-id INT [--notes]` |
| `add_interview.py` | `--application-id INT --type TYPE --scheduled-at DATETIME [--contact-id INT] [--notes]` |
| `update_application.py` | `--application-id INT --status STATUS` |
| `complete_interview.py` | `--interview-id INT --outcome OUTCOME [--notes]` |

### Queries
| Script | Key args |
|---|---|
| `upcoming_interviews.py` | `[--days INT]` (default 14) |
| `followup_contacts.py` | `[--days INT]` (default 14) |
| `application_status.py` | `[--company TEXT] [--role TEXT]` |
| `pipeline_summary.py` | none |

All scripts support `--json` for structured output.

---

## Valid Enum Values

**Application status**: `applied`, `screening`, `interviewing`, `offer`, `rejected`, `withdrawn`

**Interview type**: `phone_screen`, `technical`, `system_design`, `behavioral`, `onsite`, `take_home`

**Interview outcome**: `passed`, `failed`, `pending`

**Company status**: `active`, `inactive`, `rejected`

---

## Architecture

```
.env → config.py (Settings) → database/engine.py → database/session.py
  → repositories/ (DB queries) → services/ (business logic) → scripts/ (CLI entry points)
```

| Layer | Location | Purpose |
|---|---|---|
| Config | `src/interview_tracker/config.py` | Reads env vars |
| Engine | `src/interview_tracker/database/engine.py` | SQLAlchemy engine |
| Session | `src/interview_tracker/database/session.py` | `get_session()` context manager |
| Models | `src/interview_tracker/models/` | SQLModel table definitions |
| Schemas | `src/interview_tracker/schemas/` | Pydantic I/O models |
| Repos | `src/interview_tracker/repositories/` | All DB queries |
| Services | `src/interview_tracker/services/` | Business logic |
| Scripts | `scripts/` | CLI entry points |

---

## Changing the Database

Set `DATABASE_URL` in `.env`. The value flows through `config.py` → `engine.py` → everywhere.

- SQLite (default): `sqlite:///data/interview_tracker.db`
- Postgres: `postgresql+psycopg2://user:pass@host/dbname`

Nothing else changes.

---

## Adding FastAPI Later

1. Add `api` extra: `uv sync --extra api`
2. Create `src/interview_tracker/api/` with route files
3. Replace `with get_session() as session:` in scripts with `Depends(get_session)` in routes
4. Schema layer (`schemas/`) is already the API contract — use as `response_model=`

---

## Common Commands

```bash
uv run python scripts/init_db.py          # create/reset tables
uv run python scripts/pipeline_summary.py # show pipeline
uv run pyright src/                        # type check
uv run ruff check src/ scripts/            # lint
uv run ruff format src/ scripts/           # format
```
