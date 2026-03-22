# AGENTS.md — AI Agent Configuration for this Repository

This file defines how AI agents (GitHub Copilot, Copilot Workspace, autonomous coding agents) should behave when working in this Home Assistant repository.

---

## Repository Purpose

Self-hosted smart home infrastructure based on Home Assistant, Zigbee2MQTT, and Mosquitto MQTT. The repository manages configuration-as-code for a residential automation system.

---

## Agent Behaviour Rules

### General

- All output (code, YAML, comments, issue descriptions, PR titles) must be written in **English**
- Never generate, guess, or hallucinate entity IDs, service names, or device names — always derive them from existing config files
- Before suggesting new automations, read `homeassistant/automations.yaml` to understand existing patterns and avoid duplicates
- This is a production system. Changes to `automations.yaml`, `configuration.yaml`, or `docker-compose.yaml` affect a live home — be conservative

### Security (Non-Negotiable)

- **Never** write secrets, API keys, tokens, or passwords to any tracked file
- **Never** suggest removing `!secret` references in favour of inline values
- **Never** modify `.gitignore` in ways that could expose `secrets.yaml`, `.env`, or `data/`
- When reviewing code, always flag: hardcoded credentials, `allow_anonymous true` in MQTT, unencrypted HTTP endpoints, `privileged: true` containers
- If asked to generate a `secrets.yaml.example`, use placeholder values only — never real values

### YAML Generation

- Use **2-space indentation** for all YAML
- Follow the dot-notation alias convention: `<context>.<action>` (e.g., `bedroom.motion_lights`)
- Include `alias`, `description`, `trigger`, `condition`, and `action` keys in every automation
- Use `mode: single` unless a restart/queued/parallel mode is explicitly needed
- Template expressions must use `{{ }}` syntax — never raw Jinja without braces

### Docker / Infrastructure

- Always pin image versions. Never suggest `image: homeassistant/home-assistant:latest`
- Prefer `restart: unless-stopped` for non-critical services, `restart: always` for HA
- New services must be added to the existing `docker-compose.yaml` — do not create separate compose files

### AI / LLM Features

- When working on AI/agent features, check `homeassistant/configuration.yaml` for `assist_pipeline:` and `homeassistant/www/llmvision/` for existing LLM Vision state
- Prefer local-first AI (Ollama) over cloud APIs when writing initial implementations
- All AI-initiated HA service calls must be logged to the HA logbook with tag `[AI_AGENT]`
- Enforce rate limits on agentic loops (max 10 service calls per agent execution)
- Never allow an agent to autonomously disable the alarm or security sensors

---

## File Map for Agents

| File | Purpose | When to read |
|---|---|---|
| `homeassistant/configuration.yaml` | Main HA config | Any HA config task |
| `homeassistant/automations.yaml` | All automations | Adding/editing automations |
| `homeassistant/scripts.yaml` | Reusable scripts | Adding new scripts |
| `homeassistant/ui-lovelace.yaml` | Dashboard layout | UI/dashboard tasks |
| `homeassistant/secrets.yaml.example` | Secret key reference | When configuring integrations |
| `docker-compose.yaml` | Service definitions | Infrastructure tasks |
| `nginx.conf` | Reverse proxy config | External access / OAuth tasks |
| `cloudflared/config.yml` | Tunnel config | External access tasks |
| `data/configuration.yaml` | Zigbee2MQTT config + device list | ZigBee device tasks |
| `mosquitto_config/mosquitto.conf` | MQTT broker config | MQTT security tasks |

---

## Known Devices Reference

### Zigbee Devices (via Zigbee2MQTT → MQTT → HA)

| Friendly Name | HA Entity (auto-discovered) | Type |
|---|---|---|
| `light_1` – `light_7` | `light.light_1` – `light.light_7` | Zigbee lights |
| `button_1`, `button_2` | MQTT events | Scene controllers |
| `motion_1`, `motion_2` | `binary_sensor.motion_1_occupancy` | Motion sensors |
| `presence_1` | `binary_sensor.presence_1_*` | mmWave presence sensor |
| `door_1` | `binary_sensor.door_1_contact` | Door contact sensor |
| `window_1`, `window_2`, `window_3` | `binary_sensor.window_*_contact` | Window sensors |
| `plug_1`, `plug_2` | `switch.plug_1`, `switch.plug_2` | Smart plugs |
| `smoke_detector_1` | `binary_sensor.smoke_detector_1_smoke` | Smoke sensor |

### Non-Zigbee Devices

| Device | Integration | Key Entity |
|---|---|---|
| Tapo camera (entrance) | `tapo_control` | `camera.tapo_camera_2f13_hd_stream` |
| Tapo camera (living room) | `tapo_control` | `camera.tapo_camera_3ca0_*` |
| Xiaomi robot vacuum X20 | `xiaomi_miot` | `vacuum.xiaomi_robot_vacuum_x20_*` |
| Xiaomi air purifier MC2 | `xiaomi_miot` | `fan.zhimi_mc2_*` |
| Ender 3 V3 SE (3D printer) | `moonraker` | `sensor.ender_3_v3_se_current_print_state` |
| Yeelink color bulb | `xiaomi_miot` | `light.yeelink_color3_6f42_light` |
| Heater | Manual smart plug | `switch.smart_plug_*` |

### People

| Person | Entity | Notes |
|---|---|---|
| David (owner) | `person.destaben` | Primary notification target: `mobile_app_davids_iphone` |
| Carol | `person.carolmontaes` | Secondary occupant |

---

## Active Open Issues Summary

| # | Title | Priority |
|---|---|---|
| [#1](https://github.com/destaben/homeassistant/issues/1) | Zigbee network key in plaintext | CRITICAL |
| [#2](https://github.com/destaben/homeassistant/issues/2) | MQTT anonymous access | HIGH |
| [#3](https://github.com/destaben/homeassistant/issues/3) | nginx /auth/token blocks POST | HIGH |
| [#4](https://github.com/destaben/homeassistant/issues/4) | secrets.yaml.example invalid YAML | MEDIUM |
| [#5](https://github.com/destaben/homeassistant/issues/5) | Re-enable nginx + cloudflared | MEDIUM |
| [#6](https://github.com/destaben/homeassistant/issues/6) | Unused docker network definition | LOW |
| [#7](https://github.com/destaben/homeassistant/issues/7) | Replace manual MQTT lights with auto-discovery | MEDIUM |
| [#8](https://github.com/destaben/homeassistant/issues/8) | Add CI/CD YAML validation | MEDIUM |
| [#9](https://github.com/destaben/homeassistant/issues/9) | Container runs privileged | MEDIUM |
| [#10](https://github.com/destaben/homeassistant/issues/10) | Alarm notification with snapshot | ENHANCEMENT |
| [#11](https://github.com/destaben/homeassistant/issues/11) | Enhanced presence management | ENHANCEMENT |
| [#12](https://github.com/destaben/homeassistant/issues/12) | Smart cleaning schedule | ENHANCEMENT |
| [#13](https://github.com/destaben/homeassistant/issues/13) | Smart thermostat control | ENHANCEMENT |
| [#14](https://github.com/destaben/homeassistant/issues/14) | **EPIC**: AI Vision with LLM | AI EPIC |
| [#15](https://github.com/destaben/homeassistant/issues/15) | **EPIC**: Conversational AI + Assist | AI EPIC |
| [#16](https://github.com/destaben/homeassistant/issues/16) | **EPIC**: Agentic AI ReAct loop | AI EPIC |
| [#17](https://github.com/destaben/homeassistant/issues/17) | **EPIC**: Predictive ML automation | AI EPIC |

---

## AI Epics Roadmap

```
Q1 2026 — Foundation
├── Fix security issues (#1, #2, #3)
├── Add CI/CD validation (#8)
└── Improve existing automations (#10, #11, #12, #13)

Q2 2026 — AI Vision + Basic LLM
├── [Epic #14] LLM Vision baseline pipeline (Milestone 1-2)
├── [Epic #15] LLM conversation agent via Assist (Milestone 1-2)
└── Camera-enhanced alarm notifications

Q2-Q3 2026 — Conversational Control
├── [Epic #15] Full natural language home control (Milestone 3-4)
├── [Epic #14] Package detection & visitor log (Milestone 3)
└── Dashboard chat interface

Q3 2026 — Agentic & Predictive AI
├── [Epic #16] Tool-calling agent foundation (Milestone 1-2)
├── [Epic #17] Presence prediction & energy optimization (Milestone 1-3)
└── Anomaly detection system

Q4 2026 — Advanced Agents
├── [Epic #16] Multi-agent coordination (Milestone 4)
├── [Epic #17] Adaptive lighting + self-learning suggestions (Milestone 4-5)
└── [Epic #14] Full local Ollama vision pipeline (Milestone 4)
```

---

## Preferred Tools and Integrations for AI Features

| Feature | Recommended Integration |
|---|---|
| LLM conversation (cloud) | `openai` conversation + `extended_openai_conversation` (HACS) |
| LLM conversation (local) | `ollama` conversation integration |
| Vision analysis | `llmvision` (already installed) |
| Agent scripting | `pyscript` integration or AppDaemon |
| Long-term metrics | HA Statistics + optional InfluxDB |
| Workflow automation | n8n (optional separate container) |
| Voice pipeline | HA Assist + Whisper (local STT) + Piper (local TTS) |

---

## Contribution Guidelines for Agents

1. **Read before writing** — always read the relevant config file before suggesting changes
2. **One change at a time** — make focused, reviewable changes; avoid changing unrelated files
3. **Test instructions** — include in every PR/suggestion how to validate the change in HA
4. **Reference issues** — link to the relevant GitHub issue when making a change that addresses one
5. **Secrets stay secret** — if a new secret key is needed, add it to `secrets.yaml.example` as a placeholder and reference it with `!secret` in config
