---
name: ha-security-review
description: "Review tracked Home Assistant security, privacy, and safety behavior. Use when changing alarms, doors, windows, cameras, notifications, MQTT, network exposure, container security, or presence-linked actions."
argument-hint: "Describe the configuration slice or proposed feature to review."
user-invocable: true
---

# Home Security Review

## Checklist

1. Identify the protected asset, trigger source, action, and any state transition.
2. Verify credentials remain secret, MQTT anonymous access stays disabled, and external surfaces are intentional.
3. Review race conditions, delayed actions, retries, automation mode, unavailable states, and manual override behavior.
4. Check camera and notification behavior for privacy and data-retention implications.
5. Return findings ranked by severity, with verified evidence and safer alternatives.

## Boundary

This is a review workflow. Do not apply security-sensitive configuration changes without explicit owner approval and focused validation.