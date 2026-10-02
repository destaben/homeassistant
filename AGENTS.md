# AGENTS.md — Repository Guidance

This file defines shared rules for AI agents working on the tracked configuration and documentation in this Home Assistant repository.

## Operating Rules

- Write documentation, comments, and generated configuration in English.
- Read the relevant tracked source before making claims or changes. Never invent entity IDs, service names, device names, or integration state.
- Treat Home Assistant and infrastructure edits as production-impacting. Keep changes focused and include a validation step appropriate to the changed files.
- Do not read, copy, expose, or document values from secrets, ignored runtime state, logs, backups, or generated data. Use placeholders in examples and `!secret` references in Home Assistant configuration.
- Never modify `.gitignore` in a way that could expose secret or runtime files.
- When reviewing infrastructure, flag hardcoded credentials, anonymous MQTT access, insecure network exposure, excessive container privileges/capabilities, and weakened security settings.

## Source of Truth

Use tracked configuration for operational facts and distinguish configured behavior from live deployment state.

| Source | Authority |
|---|---|
| [docker-compose.yaml](docker-compose.yaml) | Services, image tags, mounts, ports, networks, and container settings |
| [ha/configuration.yaml](ha/configuration.yaml) | Home Assistant configuration and included files |
| [ha/automations.yaml](ha/automations.yaml) | Existing automation syntax, triggers, actions, and entity references |
| [ha/scripts.yaml](ha/scripts.yaml) | Existing script definitions |
| [ha/ui-lovelace.yaml](ha/ui-lovelace.yaml) | YAML dashboard configuration |
| [mosquitto/config/mosquitto.conf](mosquitto/config/mosquitto.conf) | Broker listener and authentication settings |
| [ha/secrets.yaml.example](ha/secrets.yaml.example) | Placeholder secret-key names only; never consult a real secrets file |

The Zigbee2MQTT runtime configuration and live Home Assistant state are not authoritative sources for tracked documentation. Verify current GitHub issues and deployment status directly when needed; otherwise label them unverified.

## Configuration Conventions

- Use two-space indentation in YAML and follow the syntax already used in the target file.
- For new automations, inspect [ha/automations.yaml](ha/automations.yaml) for nearby patterns, verify every referenced entity in tracked files, and use a descriptive dot-notation alias where the file's conventions allow it.
- Do not require optional keys or one schema spelling merely because another automation uses it; preserve compatible local patterns and validate against the configured Home Assistant version.
- Use `!secret` for credentials. Keep image versions pinned and add services to the existing Compose file.
- Keep changes conservative around alarms, access control, cameras, and other safety- or privacy-sensitive behavior.

## Documentation and AI Customizations

- [README.md](README.md) owns human-facing setup and operations; this file owns shared agent rules; [.github/copilot-instructions.md](.github/copilot-instructions.md) owns concise Copilot context.
- Before adding an AI customization, inspect the existing [agents](.github/agents/), [instructions](.github/instructions/), and [skills](.github/skills/). Add prompts or further skills only for distinct, repeatable workflows.
- The [Documentation Steward](.github/agents/documentation-steward.agent.md) is available for documentation and AI-context work. It is non-blocking and must not delay unrelated tasks.
- Use the [AI Context Audit](.github/skills/ai-context-audit/SKILL.md) skill for a repeatable review of documentation and AI customizations.
- Keep customizations scoped to a specific workflow or file. Do not add global `applyTo: "**"` instructions or lifecycle hooks.
- User-profile customizations are outside repository visibility; do not assume none exist.
