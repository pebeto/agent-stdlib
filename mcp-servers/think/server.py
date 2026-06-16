#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2.0"]
# ///
"""A `think` tool: a no-op scratchpad an agent calls to reason mid-task.

The tool changes nothing and returns nothing useful. Its only job is to give the
model a place to lay out reasoning between actions, after it has seen a tool
result and before it commits to the next one. That makes it different from
extended thinking, which happens once before the agent acts.

The pattern's value comes from how you prompt the agent to use it, not from this
file. See the `using-the-think-step` skill in this pack for when a think step
helps (analyzing tool output, policy-heavy checks, long sequential decisions)
and when it only adds latency (parallel or independent calls, simple tasks).

Run directly with uv (installs the dependency on the fly):
    uv run server.py
Or with the mcp package already installed:
    python3 server.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-stdlib-think")


@mcp.tool(
    annotations={
        "title": "Think",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def think(thought: str) -> str:
    """Record a reasoning step before the next action. Use this to work through
    a tool result, check the rules a task must follow, or plan a sequence of
    steps where an early mistake would compound. It performs no action and
    touches no state; it only gives you room to reason.

    Args:
        thought: Your reasoning. Lay out what the last result means, which
            constraints apply, and what the next action should be.
    """
    # Intentionally a no-op. The reasoning has already done its work by being
    # written; there is nothing to execute or return.
    return "Recorded. Continue with the next action."


if __name__ == "__main__":
    mcp.run()
