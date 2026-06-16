#!/usr/bin/env python3
"""A PreToolUse gate for Bash commands: tier by risk, deny or ask, never auto-allow.

This is the enforcement half of Anthropic's auto-mode pattern. An agent asked to
gate its own actions can argue itself into approval, so the gate lives in a hook
outside the model. This reference classifies a Bash command into one of three
tiers and decides:

  safe     read-only commands (ls, cat, git status, ...)  -> defer to normal flow
  unknown  anything not clearly safe or dangerous         -> ask (enforce) / allow (warn)
  dangerous destruction, exfiltration, security or trust  -> deny (enforce) / ask (warn)
           or shared-resource bypass

It never emits "allow", so it can only add friction, never remove a prompt you
would otherwise have seen.

Off by default. Set AGENT_STDLIB_GATING to turn it on:
  off (default) no-op, every command proceeds untouched
  warn          dangerous commands prompt you (ask); everything else proceeds
  enforce       dangerous commands are denied; unknown commands prompt you

This is a deterministic rule engine, not the article's two-stage LLM classifier.
Swap the rules for a classifier call when you want real judgment; keep the tiered
structure and the "deny/ask, never allow" stance. See the action-gating notes in
hooks/README.md and the sandboxing-agentic-systems skill.
"""
import json
import os
import re
import sys

MODE = os.environ.get("AGENT_STDLIB_GATING", "off").strip().lower()

GIT_SAFE = {"status", "diff", "log", "show", "branch", "remote", "rev-parse",
            "describe", "blame", "ls-files", "config", "fetch", "stash"}

SAFE_FIRST = {
    "ls", "pwd", "cat", "head", "tail", "less", "more", "grep", "rg", "ag",
    "find", "fd", "wc", "stat", "file", "which", "type", "echo", "printf",
    "date", "whoami", "id", "hostname", "uname", "df", "du", "ps", "tree",
    "env", "printenv", "sort", "uniq", "cut", "column", "diff", "jq", "yq",
    "basename", "dirname", "realpath", "readlink", "true", "test",
}

# (pattern, category, reason). First match wins.
DANGER = [
    (r"\brm\s+-[a-zA-Z]*[rf]", "destruction", "recursive or forced file deletion"),
    (r"\bdd\b", "destruction", "raw disk write with dd"),
    (r"\bmkfs", "destruction", "filesystem creation"),
    (r"\bshred\b", "destruction", "secure file erase"),
    (r">\s*/dev/(sd|nvme|disk)", "destruction", "overwrite of a block device"),
    (r":\s*\(\s*\)\s*\{", "destruction", "fork bomb"),
    (r"\bgit\b.*\b(reset\s+--hard|clean\s+-[a-zA-Z]*f|push\s+(-f|--force))",
     "destruction", "history-rewriting or force git operation"),
    (r"(curl|wget)\b[^|]*\|\s*(sudo\s+)?(sh|bash|zsh)", "security degradation",
     "piping a downloaded script straight into a shell"),
    (r"(curl|wget)\b.*(-d|--data|-T|--upload-file|-F)\b.*(\$|token|secret|key|password|\.env)",
     "exfiltration", "posting environment values or secrets to the network"),
    (r"(cat|head|tail|echo|printf)\b[^|]*(\.env|secret|token|api[_-]?key|password|id_rsa|credential)[^|]*\|\s*(curl|wget|nc)\b",
     "exfiltration", "piping a secret or credential into a network command"),
    (r"\bnc\b\s+.*-e", "exfiltration", "netcat reverse shell"),
    (r"\bchmod\s+(-R\s+)?[0-7]*7{2}\b", "security degradation", "world-writable/executable permissions"),
    (r"\bchown\s+-R\b", "security degradation", "recursive ownership change"),
    (r"\bsudo\b", "security degradation", "privilege escalation with sudo"),
    (r">>?\s*(/etc/|/usr/|/bin/|~?/?\.ssh/|.*authorized_keys)", "trust boundary",
     "writing to a system or credential path"),
    (r"\bcrontab\b|\b\.git/hooks/", "trust boundary", "installing a cron job or git hook"),
    (r"\bkill\s+-9\s+-1|\bpkill\s+-9", "shared resource", "killing every process"),
    (r"\bnpm\s+publish|\bpip\s+.*upload|\btwine\s+upload", "shared resource", "publishing a package"),
]


def classify(command: str):
    for rx, cat, reason in DANGER:
        if re.search(rx, command, re.IGNORECASE):
            return "dangerous", cat, reason
    # A compound command (pipe, chain, redirect, subshell) is not "safe" even if
    # its first token looks read-only: the dangerous part may be downstream.
    if any(op in command for op in ("|", "&&", "||", ";", "`", "$(", "\n", ">")):
        return "unknown", "", ""
    tokens = command.strip().split()
    if not tokens:
        return "safe", "", ""
    first = tokens[0]
    if first == "git":
        sub = tokens[1] if len(tokens) > 1 else ""
        return ("safe", "", "") if sub in GIT_SAFE else ("unknown", "", "")
    return ("safe", "", "") if first in SAFE_FIRST else ("unknown", "", "")


def decide(tier, reason):
    """Return a permissionDecision or None (None means defer to normal flow)."""
    if MODE == "warn":
        if tier == "dangerous":
            return "ask", f"agent-stdlib gate (warn): {reason}"
        return None
    if MODE == "enforce":
        if tier == "dangerous":
            return "deny", f"agent-stdlib gate blocked this: {reason}"
        if tier == "unknown":
            return "ask", "agent-stdlib gate: command is not on the safe list; confirm before running"
        return None
    return None  # off, or unrecognized mode


def main() -> int:
    if MODE not in ("warn", "enforce"):
        return 0  # off by default: do nothing
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        # Fail open so a parser hiccup never bricks the user's shell; say so.
        print(f"action_gate: could not parse hook input ({e}); allowing", file=sys.stderr)
        return 0
    if event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command", "")
    tier, _cat, reason = classify(command)
    result = decide(tier, reason)
    if result is None:
        return 0
    decision, message = result
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": message,
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
