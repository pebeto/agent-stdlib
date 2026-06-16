"""Example tool wrappers, presented to the agent as importable code.

The agent discovers these by listing and reading files, then writes code that
imports and composes them. Large intermediate results stay in the execution
environment; only what the code prints returns to the model's context.

Replace these with wrappers around your real tools or MCP calls.
"""
