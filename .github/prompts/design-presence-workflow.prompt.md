---
name: design-presence-workflow
description: "Design a safe Home Assistant presence or occupancy workflow without weakening security controls."
argument-hint: "Describe the presence outcome, signals, rooms, and false-positive tolerance."
---

Use the Presence Intelligence Planner and `presence-automation` skill. Build an advisory state model from tracked signals, state uncertainty and fallback behavior, and do not implement security bypasses.

Task: ${input}