"""MCP server for Interview Tracker."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp.server.fastmcp import FastMCP
from tools.applications import register as register_applications
from tools.companies import register as register_companies
from tools.contacts import register as register_contacts
from tools.interviews import register as register_interviews

from interview_tracker.database.engine import init_db

init_db()

mcp = FastMCP("Interview Tracker")

register_applications(mcp)
register_interviews(mcp)
register_contacts(mcp)
register_companies(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
