---
name: ai-vision-roadmap
description: "Plan privacy-conscious Home Assistant camera and AI vision capabilities. Use when considering camera analysis, LLM vision, package or visitor detection, reference images, event summaries, or vision-driven automations."
argument-hint: "Describe the desired camera outcome, privacy constraints, retention expectations, and allowed follow-up actions."
user-invocable: true
---

# AI Vision Roadmap

## Procedure

1. Establish the explicit objective, allowed cameras, retention policy, and notification audience.
2. Verify tracked camera configuration and existing integration boundaries; do not inspect snapshots or ignored media.
3. Prefer event-driven analysis, bounded request rates, and human-readable audit records.
4. Define confidence thresholds, safe fallback behavior, and a review path for false detections.
5. Start with advisory notifications; do not let vision output directly disable security or control physical access.

## Privacy

Minimize captures, keep data local where practical, never embed image contents in tracked files, and require explicit approval before adding cloud analysis.