---
name: Home Assistant Automation Guidance
description: Source-backed guidance for editing this repository's Home Assistant automations.
applyTo: "ha/automations.yaml"
---

# Home Assistant Automations

- Read the existing automation list and nearby entries before editing. Preserve local structure unless the requested change requires otherwise.
- Verify entity IDs, device IDs, event types, and service/action names from tracked configuration. Never guess them; report references that cannot be verified from tracked sources.
- Follow the Home Assistant automation syntax already used in the file. Existing entries use both legacy and newer key spellings and do not all contain identical optional keys, so do not normalize unrelated entries or impose a fixed key checklist.
- Use a clear dot-notation alias for new entries when it fits the existing naming patterns. Preserve an existing stable `id` when updating an automation.
- Keep behavior changes narrow, especially for alarm/security behavior, physical access, cameras, and presence detection. Do not add AI-driven actions that disable alarms or security sensors.
- Keep credentials out of automation YAML; use `!secret` where a secret is required.
- Validate with the repository's configured `yamllint` command and, when available, Home Assistant's configuration check. A YAML lint pass does not prove that entities or device-registry references resolve in the live instance.