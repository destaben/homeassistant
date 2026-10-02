---
name: presence-automation
description: "Design and review safe Home Assistant presence and occupancy automation. Use when working with people, motion, door, window, presence sensors, arrivals, departures, room occupancy, or context-aware behavior."
argument-hint: "Describe the desired presence behavior, source signals, and false-positive tolerance."
user-invocable: true
---

# Presence Automation

## Procedure

1. List verified signals separately: household location, room presence, motion, doors, windows, and timers.
2. Define the intended state machine, including unknown/unavailable states, debounce intervals, and stale-signal handling.
3. Start with advisory or reversible actions such as lighting, climate presets, or notifications.
4. For each proposed automation, state the false-positive impact and a manual override path.
5. Require owner confirmation and a security review before using presence in any alarm, camera, or access-control workflow.

## Never Do

- Infer presence from untracked device state.
- Treat a single transition as definitive household state without a fallback.
- Automatically disarm alarms, unlock access, or suppress security notifications.