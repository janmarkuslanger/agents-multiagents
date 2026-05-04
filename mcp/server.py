"""MCP server exposing the agents-multiagent workflow as tools.

Usage (stdio transport, default):
    python server.py

Usage (SSE transport, for remote access):
    python server.py --transport sse --port 8000

Add to Claude Code via ~/.claude.json or project .claude/settings.json:
    {
      "mcpServers": {
        "agents-multiagent": {
          "command": "python",
          "args": ["/path/to/agents/mcp/server.py"]
        }
      }
    }
"""
from mcp.server.fastmcp import FastMCP
import anthropic
from pathlib import Path

mcp = FastMCP("agents-multiagent")
BASE = Path(__file__).parent.parent
MODEL = "claude-sonnet-4-6"


def _load_role(name: str) -> str:
    return (BASE / f"{name}.md").read_text()


def _call(system: str, user: str) -> str:
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


@mcp.tool()
def run_architect(
    requirements: str,
    quality_requirements: str = "",
    constraints: str = "",
) -> str:
    """Run the Software Architect to produce a design document (JSON).

    Pass the returned JSON string to run_coder as design_document_json.
    """
    parts = [
        "Automated session. Skip quality/constraint questions and the skip-architect"
        " question. Produce the design document JSON directly without waiting for"
        " confirmation.",
        f"Requirements:\n{requirements}",
    ]
    if quality_requirements:
        parts.append(f"Quality requirements: {quality_requirements}")
    if constraints:
        parts.append(f"Constraints: {constraints}")
    return _call(_load_role("architect"), "\n\n".join(parts))


@mcp.tool()
def run_coder(design_document_json: str) -> str:
    """Run the Coder to implement the confirmed design document.

    Pass the Architect's JSON output as design_document_json.
    Returns implementation JSON. Pass the result to run_reviewer.
    """
    return _call(
        _load_role("coder"),
        f"Confirmed design document:\n{design_document_json}",
    )


@mcp.tool()
def run_reviewer(design_document_json: str, coder_output_json: str) -> str:
    """Run the Reviewer to verify the implementation against the design.

    Returns verdict JSON with fields: verdict, critical_issues, suggestions,
    notes, design_gaps.
    """
    return _call(
        _load_role("reviewer"),
        f"Design document:\n{design_document_json}\n\nImplementation:\n{coder_output_json}",
    )


@mcp.tool()
def run_tester(design_document_json: str, coder_output_json: str) -> str:
    """Run the Tester to assess test coverage of the implementation.

    Optional role. Insert between Coder and Reviewer.
    Returns verdict JSON with fields: coverage_assessment, missing_tests,
    verdict, notes.
    """
    tester_path = BASE / "tester.md"
    if not tester_path.exists():
        return '{"error": "tester.md not found. Add it to your project or agents/tester.md."}'
    return _call(
        tester_path.read_text(),
        f"Design document:\n{design_document_json}\n\nImplementation:\n{coder_output_json}",
    )


if __name__ == "__main__":
    mcp.run()
