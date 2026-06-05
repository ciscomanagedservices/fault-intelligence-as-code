"""
app — Fault Intelligence Webhook Relay.

Minimal FastAPI service that bridges Splunk fault alert webhooks and Webex
approval callbacks to an OpenCode server running the fault-remediation skill.

The LLM agent logic lives in the OpenCode skill (.opencode/skills/fault-remediation/SKILL.md),
not in Python code. This package provides:

  - alert_pipeline.py — webhook relay (Splunk -> OpenCode, Webex callbacks)

Architecture:
  Splunk webhook -> alert_pipeline.py -> OpenCode session -> fault-remediation skill
                                                          -> RADKit MCP (device CLI)
                                                          -> Webex REST API (notifications)
"""

from __future__ import annotations

__version__ = "0.2.0"
