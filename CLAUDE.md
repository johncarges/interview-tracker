# Interview Tracker — Claude's Operating Manual

## What This App Does

Local-first interview tracking. Data lives in a SQLite file at `data/interview_tracker.db`.
The primary interface is natural language — describe what you want, and either run a convenience
script or write a short ad-hoc Python snippet using the service/repository layer directly.

---

## One-Time Setup

```bash
uv sync --extra dev
cp .env.example .env          # already done if .env exists
uv run python scripts/init_db.py
```

---

## Two Ways to Interact

### 1. Convenience scripts — for mutations and common queries

Use pre-built scripts for operations with side effects (validation, status changes) and
for the most frequent read operations.

```bash
uv run python scripts/add_company.py "Stripe" --industry fintech
uv run python scripts/pipeline_summary.py
uv run python scripts/upcoming_interviews.py --days 7
```

### 2. Ad-hoc Python — for flexible, one-off queries

For anything not covered by a script, write a short Python snippet directly. The service
and repository layers are the real API — use them freely.

```python
import sys; sys.path.insert(0, "src")
from interview_tracker.database.session import get_session
from interview_tracker.repositories.company import CompanyRepository
from interview_tracker.repositories.role import RoleRepository
from interview_tracker.repositories.application import ApplicationRepository

with get_session() as session:
    companies = CompanyRepository(session).list_all()
    edtech = [c for c in companies if c.industry == "edtech"]
    for company in edtech:
        roles = RoleRepository(session).list_by_company(company.id)
        unapplied = [r for r in roles if not ApplicationRepository(session).list_by_role(r.id)]
        for role in unapplied:
            print(f"{company.name} — {role.title}")
```

If a query pattern comes up repeatedly, it's a candidate to become a new convenience script.

---

## Convenience Script Reference

### Mutations
| Script | Key args |
|---|---|
| `init_db.py` | none |
| `add_company.py` | `NAME [--website] [--industry] [--status] [--notes]` |
| `add_contact.py` | `NAME --company TEXT [--title] [--email] [--phone] [--linkedin] [--notes]` |
| `add_role.py` | `TITLE --company TEXT [--url] [--salary-min] [--salary-max] [--notes]` |
| `add_application.py` | `[--role-id INT] [--company TEXT] [--role TEXT] [--notes]` |
| `add_interview.py` | `--application-id INT --type TYPE --scheduled-at DATETIME [--contact-id INT]` |
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
.env → config.py → database/engine.py → database/session.py
  → repositories/ (DB queries)
    → services/ (business logic)
      → scripts/ (convenience CLI entry points)
         ↕
      ad-hoc Python (flexible queries)
```

| Layer | Location | Purpose |
|---|---|---|
| Models | `src/interview_tracker/models/` | SQLModel table definitions |
| Schemas | `src/interview_tracker/schemas/` | Pydantic I/O models |
| Repos | `src/interview_tracker/repositories/` | All DB queries |
| Services | `src/interview_tracker/services/` | Business logic |
| Scripts | `scripts/` | Convenience CLI entry points |

---

## Changing the Database

Set `DATABASE_URL` in `.env`. Nothing else changes.

- SQLite (default): `sqlite:///data/interview_tracker.db`
- Postgres: `postgresql+psycopg2://user:pass@host/dbname`

---

## Common Commands

```bash
uv run python scripts/init_db.py          # create/reset tables
uv run python scripts/pipeline_summary.py # show pipeline
uv run pyright src/                        # type check
uv run ruff check src/ scripts/            # lint
uv run ruff format src/ scripts/           # format
```
