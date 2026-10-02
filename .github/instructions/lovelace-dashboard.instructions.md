---
name: Lovelace Dashboard Configuration
description: Source-backed guidance for the repository's YAML-mode Home Assistant dashboard.
applyTo: "ha/ui-lovelace.yaml"
---

# Lovelace Dashboard Configuration

- Verify every entity and script reference from tracked configuration before adding a card.
- Preserve the existing sections-based layout and local YAML style.
- Design for frequent operational use: clear room grouping, stable controls, and visible state.
- Avoid exposing sensitive camera, alarm, or access controls without explicit owner direction.
- Validate YAML and review the view in a running Home Assistant instance before relying on it.