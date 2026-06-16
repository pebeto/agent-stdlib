#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2.0"]
# ///
"""A tool-search gateway: many tools behind two.

A large tool library bloats an agent's context, because every tool definition
sits in the window whether the task needs it or not. This server keeps the
client's context small by exposing only two tools, `search_tools` and
`call_tool`, while holding a larger catalog behind them. The agent searches for
what it needs, reads only those definitions, then invokes them by name. That is
the server-side half of progressive disclosure from Anthropic's tool-use work.

The catalog here holds a few dependency-free example tools so the server runs
and tests on its own. Replace `CATALOG` with your real tools, or adapt
`call_tool` to proxy to downstream MCP servers, to use it for real.

Source: Advanced tool use
(https://www.anthropic.com/engineering/advanced-tool-use) and Code execution
with MCP (https://www.anthropic.com/engineering/code-execution-with-mcp).

Run:
    uv run server.py
"""
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-stdlib-tool-gateway")


# --- example tool implementations (pure standard library) -------------------

def _text_stats(text: str) -> dict:
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": text.count("\n") + 1 if text else 0,
    }


def _temp_convert(value: float, from_unit: str, to_unit: str) -> dict:
    f, t = from_unit.upper(), to_unit.upper()
    units = {"C", "F", "K"}
    if f not in units or t not in units:
        raise ValueError(f"units must be one of {sorted(units)}, got {from_unit!r}->{to_unit!r}")
    celsius = {"C": value, "F": (value - 32) * 5 / 9, "K": value - 273.15}[f]
    out = {"C": celsius, "F": celsius * 9 / 5 + 32, "K": celsius + 273.15}[t]
    return {"value": round(out, 4), "unit": t}


def _base_convert(number: str, from_base: int, to_base: int) -> dict:
    if not (2 <= from_base <= 36 and 2 <= to_base <= 36):
        raise ValueError("bases must be between 2 and 36")
    n = int(str(number), from_base)
    if n == 0:
        return {"result": "0", "base": to_base}
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out, neg = "", n < 0
    n = abs(n)
    while n:
        out = digits[n % to_base] + out
        n //= to_base
    return {"result": ("-" if neg else "") + out, "base": to_base}


def _json_validate(text: str) -> dict:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        return {"valid": False, "error": str(e)}
    return {"valid": True, "pretty": json.dumps(parsed, indent=2, sort_keys=True)}


# --- the catalog held behind the gateway ------------------------------------

CATALOG = {
    "text_stats": {
        "description": "Count the characters, words, and lines in a piece of text.",
        "schema": {"text": "string — the text to measure"},
        "fn": _text_stats,
    },
    "temp_convert": {
        "description": "Convert a temperature between Celsius, Fahrenheit, and Kelvin.",
        "schema": {
            "value": "number — the temperature to convert",
            "from_unit": "string — C, F, or K",
            "to_unit": "string — C, F, or K",
        },
        "fn": _temp_convert,
    },
    "base_convert": {
        "description": "Convert an integer from one numeric base to another (2 to 36).",
        "schema": {
            "number": "string — the integer, written in from_base",
            "from_base": "integer — 2 to 36",
            "to_base": "integer — 2 to 36",
        },
        "fn": _base_convert,
    },
    "json_validate": {
        "description": "Check whether a string is valid JSON and pretty-print it.",
        "schema": {"text": "string — the JSON text to validate"},
        "fn": _json_validate,
    },
}


def _score(query: str, name: str, description: str) -> int:
    """Rank a catalog entry against the query by term overlap, with a bonus for
    a substring hit. Simple on purpose; swap in BM25 or embeddings for scale."""
    q = query.lower()
    haystack = f"{name} {description}".lower()
    score = sum(1 for term in q.split() if term in haystack)
    if q in haystack:
        score += 2
    return score


@mcp.tool(annotations={"title": "Search tools", "readOnlyHint": True, "openWorldHint": False})
def search_tools(query: str, detail: str = "summary") -> str:
    """Find tools in the catalog that match a query, without loading every
    definition into context. Start here, then call the matches by name.

    Args:
        query: What you want to do, in plain words (e.g. "convert temperature").
        detail: "summary" returns names and descriptions; "full" also returns
            each tool's argument schema.
    """
    ranked = sorted(
        ((name, _score(query, name, e["description"]), e) for name, e in CATALOG.items()),
        key=lambda x: x[1],
        reverse=True,
    )
    hits = [(name, e) for name, s, e in ranked if s > 0] or [(name, e) for name, s, e in ranked]
    out = []
    for name, e in hits:
        item = {"name": name, "description": e["description"]}
        if detail == "full":
            item["arguments"] = e["schema"]
        out.append(item)
    return json.dumps(out, indent=2)


@mcp.tool(annotations={"title": "Call tool", "openWorldHint": False})
def call_tool(name: str, arguments: dict) -> str:
    """Invoke a catalog tool by name. Use `search_tools` first to find the name
    and its arguments.

    Args:
        name: The tool name returned by search_tools.
        arguments: The tool's arguments as a JSON object.
    """
    entry = CATALOG.get(name)
    if entry is None:
        return json.dumps({
            "error": f"unknown tool {name!r}",
            "hint": "call search_tools to list available tools",
            "available": sorted(CATALOG),
        })
    try:
        result = entry["fn"](**arguments)
    except TypeError as e:
        return json.dumps({
            "error": f"bad arguments for {name!r}: {e}",
            "expected": entry["schema"],
        })
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})
    return json.dumps({"tool": name, "result": result})


if __name__ == "__main__":
    mcp.run()
