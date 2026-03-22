# GitHub Copilot Workspace Instructions

## Project Overview

This is a **self-hosted Home Assistant smart home** running on Docker Compose. The stack consists of:

- **Home Assistant** (`homeassistant/`) — core automation platform (v2026.2+)
- **Zigbee2MQTT** (`data/`) — Zigbee mesh coordinator via Sonoff 3.0 USB dongle
- **Eclipse Mosquitto** (`mosquitto_config/`, `etc_mosquitto/`) — MQTT broker
- **nginx** (`nginx.conf`) — security reverse proxy for Google Assistant OAuth
- **Cloudflared** (`cloudflared/`) — Cloudflare tunnel for external access

## Repository Layout

```
homeassistant/          # HA config (mapped to /config inside container)
  configuration.yaml    # Main HA config — lovelace, http, mqtt, templates
  automations.yaml      # All automations (flat list, not split by room)
  scripts.yaml          # Reusable scripts (camera presets)
  scenes.yaml           # Scene definitions (currently empty)
  ui-lovelace.yaml      # Dashboard layout in YAML mode
  secrets.yaml          # Real secrets — NEVER commit this file
  secrets.yaml.example  # Template for secrets — keep in sync with actual keys
  custom_components/    # HACS and custom integrations (gitignored)
data/                   # Zigbee2MQTT state (gitignored — contains network key)
mosquitto_config/       # Mosquitto static config
docker-compose.yaml     # All services definition
nginx.conf              # Reverse proxy config for Google Assistant
cloudflared/config.yml  # Cloudflare tunnel config
```

## Key Conventions

### YAML Style
- Use 2-space indentation throughout all YAML files
- Quote all string values in automations/scripts unless they are entity IDs or service names
- Group related automations with a dot-notation alias prefix: `door.opened`, `presence.welcome_home`, `alarm.security_alert`
- Use `!secret` for all credentials, API keys, and sensitive values

### Entity Naming
- Zigbee devices: `light_1` through `light_7`, `motion_1`, `motion_2`, `door_1`, `button_1`, `button_2`, `plug_1`, `plug_2`, `presence_1`, `window_1/2/3`
- Persons: `person.destaben` (David), `person.carolmontaes` (Carol)
- Notification target: `mobile_app_davids_iphone`
- Camera: `camera.tapo_camera_2f13_hd_stream` (entrance), `camera.tapo_camera_3ca0_*` (living room)
- Vacuum: `vacuum.xiaomi_robot_vacuum_x20_*`
- Air purifier: `fan.zhimi_mc2_*`

### Security Rules
- **Never** add credentials, tokens, keys, or passwords to any tracked file
- **Never** commit `homeassistant/secrets.yaml` (it is gitignored)
- **Never** commit `data/configuration.yaml` (contains Zigbee network key, gitignored)
- **Never** commit `.env` (contains Cloudflare tunnel token, gitignored)
- MQTT topics follow `zigbee2mqtt/<friendly_name>` convention

### Docker Compose
- Pin image versions explicitly (e.g., `2026.2` not `latest`)
- Use `restart: always` for HA, `restart: unless-stopped` for supporting services
- Secrets and tokens go in `.env` (never hardcoded in `docker-compose.yaml`)

## Custom Components Available

| Component | Purpose |
|---|---|
| `bluetti_bt` | Bluetti power station Bluetooth |
| `dreame_vacuum` | Dreame/Xiaomi robot vacuum |
| `edata` | Spanish electricity consumption (PVPC) |
| `hacs` | Community store |
| `meross_lan` | Meross LAN devices |
| `meshtastic` | LoRa mesh radio integration |
| `moonraker` | 3D printer (Klipper/Moonraker — Ender 3 V3 SE) |
| `tapo_control` | TP-Link Tapo cameras (PTZ control, snapshots) |
| `xiaomi_miot` | Xiaomi IoT devices (purifier, vacuum) |
| `llmvision` | LLM-powered camera analysis (installed in `llmvision/`) |

## AI & Agent Context

The AI/agent features in this project are actively being developed. Key facts:

- `assist_pipeline:` is already enabled in `configuration.yaml`
- `llmvision` integration stores snapshots in `homeassistant/www/llmvision/`
- Camera reference images are in `homeassistant/www/llmvision/reference/`
- Voice assistant is handled via HA's Assist pipeline + external LLM backend
- Agentic automations use the ReAct pattern: Read sensor → Reason → Act → Verify

When working on AI features, prefer:
1. Local Ollama over cloud APIs when latency allows
2. `extended_openai_conversation` HACS integration for LLM-backed Assist
3. `pyscript` or AppDaemon for custom agent logic

## Testing Approach

There is no automated test suite. Changes are validated by:
1. `docker compose config --quiet` — validate docker-compose syntax
2. `yamllint homeassistant/*.yaml` — YAML syntax check
3. Home Assistant's built-in **Developer Tools → YAML → Check Configuration** — validates HA config
4. `docker compose restart homeassistant` — live reload for config changes

## Common Tasks

### Adding a new Zigbee device
1. Pair device via Zigbee2MQTT dashboard (port 8082)
2. Set a `friendly_name` matching the naming convention
3. Device auto-discovers in HA — no manual config needed
4. Add to `automations.yaml` as needed

### Adding a new automation
1. Add to `homeassistant/automations.yaml`
2. Use dot-notation alias: `<domain>.<action>` (e.g., `bedroom.motion_lights`)
3. Use `!secret` for any sensitive values
4. Test via Developer Tools → Services in HA UI

### Re-enabling Google Assistant
1. Fix `/auth/token` POST method in `nginx.conf` (see issue #3)
2. Set `CLOUDFLARE_TUNNEL_TOKEN` in `.env`
3. Uncomment nginx + cloudflared services in `docker-compose.yaml`
4. Run `docker compose up -d nginx cloudflared`
