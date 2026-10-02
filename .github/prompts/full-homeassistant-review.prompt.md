---
name: full-homeassistant-review
description: "Run a structured Home Assistant repository review across automation quality, presence, security, Assist readiness, dashboard, documentation, and validation."
argument-hint: "Describe the review scope or leave blank for the tracked configuration baseline."
---

Use the Home Automation Orchestrator. First delegate read-only reviews to the security, presence, dashboard, Assist, and documentation specialists. Synthesize verified findings, recommendations, and validation gaps only; do not implement changes during a review. Handle any requested implementation as a separate task through the appropriate configuration owner. Report deferred live-system checks separately.

Scope: ${input}