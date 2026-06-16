#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2.0"]
# ///
"""Code execution over MCP: tools as importable code, composed in a sandbox.

Instead of loading every tool definition into context, this server presents
tools as files the agent discovers and reads on demand, then lets the agent
write Python that imports and composes them. Large intermediate results stay in
the execution environment; only what the code prints returns to the model. That
is the pattern from Anthropic's "Code execution with MCP" post.

Three tools:
  list_tools()        discover the available tool modules
  read_tool(name)     read one module's source (progressive disclosure)
  run_python(code)    execute code with the tools package importable

Security note: run_python executes model-written code. The server applies a
wall-clock timeout, POSIX resource limits (CPU, memory, file size), and a
temporary working directory, but treat it as a reference rather than a hardened
sandbox. It does not isolate the network or the wider filesystem. Wrap it in
real OS-level isolation before running it on anything you care about. The
`sandboxing-agentic-systems` skill in this pack describes how: filesystem and
network isolation that covers subprocesses, an egress proxy, and credentials
kept outside the sandbox.

Source: https://www.anthropic.com/engineering/code-execution-with-mcp

Run:
    uv run server.py
"""
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-stdlib-code-execution")

SERVER_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SERVER_DIR / "tools"

TIMEOUT_CAP_SECONDS = 60
MEM_LIMIT_BYTES = 512 * 1024 * 1024   # 512 MB address space
FSIZE_LIMIT_BYTES = 10 * 1024 * 1024  # 10 MB per file written


def _first_docstring_line(path: Path) -> str:
    """Cheap one-line summary: the module's opening docstring line."""
    try:
        text = path.read_text()
    except OSError:
        return ""
    marker = '"""'
    start = text.find(marker)
    if start == -1:
        return ""
    rest = text[start + 3:]
    end = rest.find(marker)
    body = (rest if end == -1 else rest[:end]).strip()
    return body.splitlines()[0] if body else ""


@mcp.tool(annotations={"title": "List tools", "readOnlyHint": True, "openWorldHint": False})
def list_tools() -> str:
    """List the tool modules available to import in run_python. Start here, then
    read_tool the ones you need before writing code."""
    mods = []
    for p in sorted(TOOLS_DIR.glob("*.py")):
        if p.name == "__init__.py":
            continue
        mods.append(f"tools.{p.stem}: {_first_docstring_line(p)}")
    header = ("Import these in run_python, e.g. `from tools import text_utils`.\n"
              "Read a module with read_tool before using it.\n\n")
    return header + "\n".join(mods)


@mcp.tool(annotations={"title": "Read tool", "readOnlyHint": True, "openWorldHint": False})
def read_tool(name: str) -> str:
    """Return the source of a tool module so you can see its functions and
    signatures before composing them.

    Args:
        name: The module, with or without the `tools.` prefix (e.g.
            "text_utils" or "tools.text_utils").
    """
    stem = name.split(".")[-1]
    path = TOOLS_DIR / f"{stem}.py"
    if not path.exists() or path.name == "__init__.py":
        available = [f"tools.{p.stem}" for p in TOOLS_DIR.glob("*.py") if p.name != "__init__.py"]
        return f"no tool module {name!r}. available: {sorted(available)}"
    return path.read_text()


def _posix_limits():
    """Cap CPU, memory, and file size for the child. POSIX only; a no-op
    elsewhere. Runs in the child after fork, before exec."""
    try:
        import resource
    except ImportError:
        return
    cpu = TIMEOUT_CAP_SECONDS + 1
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT_BYTES, MEM_LIMIT_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (FSIZE_LIMIT_BYTES, FSIZE_LIMIT_BYTES))


@mcp.tool(annotations={"title": "Run Python", "readOnlyHint": False, "openWorldHint": True})
def run_python(code: str, timeout_seconds: int = 10) -> str:
    """Execute Python code with the tools package importable, and return its
    stdout and stderr. Import what you need (`from tools import math_utils`), do
    the heavy work here, and print only the result you want back; large
    intermediate data should stay in this environment, not flow into context.

    Args:
        code: The Python source to run.
        timeout_seconds: Wall-clock limit, capped at 60.
    """
    timeout = max(1, min(int(timeout_seconds), TIMEOUT_CAP_SECONDS))
    import tempfile
    with tempfile.TemporaryDirectory(prefix="agent-stdlib-exec-") as workdir:
        main = Path(workdir) / "main.py"
        main.write_text(code)
        env = {
            "PYTHONPATH": str(SERVER_DIR),  # makes `from tools import ...` work
            "PATH": "/usr/bin:/bin",
            "HOME": workdir,
        }
        try:
            proc = subprocess.run(
                [sys.executable, "-s", str(main)],
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=_posix_limits if sys.platform != "win32" else None,
            )
        except subprocess.TimeoutExpired:
            return f"TIMEOUT: code exceeded {timeout}s and was killed."
        parts = []
        if proc.stdout:
            parts.append("STDOUT:\n" + proc.stdout)
        if proc.stderr:
            parts.append("STDERR:\n" + proc.stderr)
        parts.append(f"(exit code {proc.returncode})")
        return "\n".join(parts)


if __name__ == "__main__":
    mcp.run()
