---
name: ha-feature-delivery
description: "Deliver a focused Home Assistant feature from evidence-backed design through implementation and validation. Use when adding or changing automations, scripts, configuration, scenes, or MQTT-backed behavior."
argument-hint: "Describe the requested behavior and any verified entities, services, or automation aliases."
user-invocable: true
---

# Home Assistant Feature Delivery

## Procedure

1. Read the target file, [shared guidance](../../../AGENTS.md), and nearby examples.
2. Create a behavior brief with trigger, conditions, actions, mode, failure behavior, and validation.
3. Verify every reference from tracked files. Do not use ignored runtime configuration, secrets, logs, or device registries.
4. For alarms, cameras, access, presence, or external notification behavior, perform a security review before implementation.
5. Apply the smallest focused YAML change; preserve IDs and unrelated style.
6. Run YAML lint and Home Assistant configuration validation when available. Run Compose validation only if Compose changed.
7. Report changed behavior, deferred live checks, and rollback scope.

## Guardrails

- Never deploy, restart, reload, or invoke live Home Assistant services.
- Never create actions that automatically disable alarms or security sensors.
- Use `!secret` for credentials and do not add new real values to tracked files.