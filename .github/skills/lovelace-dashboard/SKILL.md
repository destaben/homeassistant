---
name: lovelace-dashboard
description: "Build or review the YAML-mode Home Assistant dashboard. Use when changing views, sections, cards, entity controls, room layouts, camera panels, or operational observability."
argument-hint: "Describe the target dashboard workflow, room, and verified entities."
user-invocable: true
---

# Lovelace Dashboard

## Procedure

1. Map the daily user workflow and verify the available entities.
2. Group controls by room and urgency; place safety-relevant state where it can be scanned quickly.
3. Use native cards and existing custom cards before adding dependencies.
4. Ensure primary actions have stable dimensions, direct feedback, and no overlap.
5. Validate YAML and review the view in a running Home Assistant instance before relying on it operationally.

## Safety

Avoid one-tap controls for security-sensitive behavior unless the owner explicitly requests them and understands the effect.