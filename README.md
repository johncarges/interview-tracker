# Interview Tracker

A local-first job search tracker with an MCP server for Claude Code. Describe what you want
in natural language and Claude handles it — no commands needed. Data lives in a local SQLite
file.

---

## MCP Setup

Requires [Claude Code](https://claude.ai/code) and [uv](https://docs.astral.sh/uv/).

Install uv if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open Terminal (on Mac: press `Cmd+Space`, type "Terminal", press Enter), then run:

```bash
# 1. Get the code (skip if you already have the folder)
git clone https://github.com/johncarges/interview-tracker

# 2. Navigate into the folder
cd interview-tracker

# 3. Register the MCP
claude mcp add -s user interview-tracker -- uv --directory "$(pwd)" run mcp_server/server.py
```

> **Tip:** If you downloaded a zip instead of cloning, drag the unpacked folder into the Terminal
> window after step 1 to paste its path, then press Enter to navigate into it.

The `-s user` flag registers the MCP globally — you can use Claude from any directory after this.
The database is created automatically on first run. Once connected, just talk to Claude:

> *"Add a role at Google for Backend Engineer and mark me as applied"*
> *"What's my pipeline looking like?"*
> *"Are there any interviews coming up this week?"*
> *"Update my Meta application to screening"*

---

## Script Usage

If you want to use the CLI scripts directly without the MCP:

```bash
git clone https://github.com/johncarges/interview-tracker
cd interview-tracker
uv sync
uv run python scripts/init_db.py
```

Then run scripts directly:

```bash
uv run python scripts/pipeline_summary.py
uv run python scripts/upcoming_interviews.py --days 7
uv run python scripts/add_company.py "Acme Corp" --industry fintech
```

---

## Architecture

- **MCP server** (`mcp_server/`): exposes tools Claude calls directly
- **Scripts** (`scripts/`): thin CLI wrappers around the same service layer
- **Service layer** (`src/`): all business logic, repositories, and database access
- **Storage**: SQLite, a single local file at `data/interview_tracker.db`

The storage and client layers are decoupled — `DATABASE_URL` in `.env` can be pointed at
Postgres without changing anything else, and a future FastAPI layer would just call the same
services used today.
