# Copilot Repository Context

Shared safety rules and source ownership are in [AGENTS.md](../AGENTS.md). This file is intentionally concise; do not treat it as a live inventory of devices or integrations.

## Verified Repository Context

- [docker-compose.yaml](../docker-compose.yaml) defines Home Assistant `2026.9.4`, Zigbee2MQTT `2.8.0`, and Mosquitto `2.0`. It does not define nginx or Cloudflared.
- [ha/configuration.yaml](../ha/configuration.yaml) is the Home Assistant entry point. It includes automations and scripts and currently declares `assist_pipeline:`.
- [mosquitto/config/mosquitto.conf](../mosquitto/config/mosquitto.conf) disables anonymous access and requires a password file. Never document or expose credential values.
- [.github/workflows/validate.yml](workflows/validate.yml) is the source of truth for automated validation and its triggers.

## Working Rules

- Read the tracked file being changed and nearby examples. Derive entity and service references from tracked configuration; do not guess or use ignored runtime data.
- Follow existing YAML syntax in the target file. For automation-specific guidance, see [home-assistant-automations.instructions.md](instructions/home-assistant-automations.instructions.md).
- Treat configuration changes as production-impacting. Do not restart or alter a live deployment unless explicitly requested.
- Do not assume integrations, entity registries, issue status, or deployment state from repository context. Check the live source or mark the fact unverified.
- For documentation and AI-context work, the [Documentation Steward](agents/documentation-steward.agent.md) is available and non-blocking.
- Use the [AI Context Audit](skills/ai-context-audit/SKILL.md) skill for a repeatable documentation and customization review.
