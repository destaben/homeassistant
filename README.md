# Home Assistant — Configuration as Code

Self-hosted smart home running on Docker Compose. This repository is a full disaster-recovery snapshot of all configuration.

## Stack

| Service | Image | Role |
|---|---|---|
| Home Assistant | `ghcr.io/home-assistant/home-assistant:2026.2` | Core platform |
| Zigbee2MQTT | `koenkk/zigbee2mqtt:2.8.0` | Zigbee coordinator (Sonoff 3.0 USB) |
| Mosquitto | `eclipse-mosquitto:2.0` | MQTT broker |
| nginx | `nginx:stable` | Security reverse proxy for Google Assistant OAuth *(disabled)* |
| Cloudflared | `cloudflare/cloudflared` | External tunnel via `hassistant.destaben.dev` *(disabled)* |

> nginx and cloudflared are currently commented out in `docker-compose.yaml`. See [#5](https://github.com/destaben/homeassistant/issues/5) to re-enable.

## Repository Layout

```
homeassistant/              # HA config (bind-mounted to /config in container)
  configuration.yaml        # HTTP, MQTT switches, templates, integrations
  automations.yaml          # All automations (dot-notation aliases)
  scripts.yaml              # Reusable scripts (camera presets)
  scenes.yaml               # Scene definitions
  ui-lovelace.yaml          # YAML-mode dashboard
  secrets.yaml.example      # Secret key template — copy to secrets.yaml
  secrets.yaml              # ⚠️ NOT versioned — contains real credentials
  custom_components/        # ⚠️ NOT versioned — installed via HACS
  blueprints/               # ⚠️ NOT versioned
  www/                      # ⚠️ NOT versioned — LLM Vision snapshots, etc.

data/                       # ⚠️ NOT versioned — Zigbee2MQTT state + network key
mosquitto_config/           # Mosquitto static config (versioned)
etc_mosquitto/              # ⚠️ NOT versioned — runtime certs/passwd
nginx.conf                  # Reverse proxy config (versioned)
cloudflared/config.yml      # Tunnel config (versioned)
docker-compose.yaml         # All service definitions (versioned)
.env.example                # Env var template — copy to .env
.env                        # ⚠️ NOT versioned — Cloudflare tunnel token
AGENTS.md                   # AI agent rules and device reference
.github/
  copilot-instructions.md   # GitHub Copilot workspace context
  workflows/validate.yml    # CI: yamllint + docker-compose + HA config check
  ISSUE_TEMPLATE/           # Bug, feature, security issue templates
```

## Disaster Recovery

### 1. Clone

```bash
git clone https://github.com/destaben/homeassistant.git
cd homeassistant
```

### 2. Create secrets

```bash
cp .env.example .env
# Edit .env — add CLOUDFLARE_TUNNEL_TOKEN and Zigbee secrets (see below)

cp homeassistant/secrets.yaml.example homeassistant/secrets.yaml
# Edit secrets.yaml — add all credentials
```

### 3. Set Zigbee2MQTT network secrets

The Zigbee network encryption key, PAN ID, and Extended PAN ID are supplied via
environment variables so they never need to be stored in `data/configuration.yaml`.
Set these in your `.env` file:

```bash
# Generate a new 16-byte network key (if setting up from scratch):
python3 -c "import os, json; print(json.dumps(list(os.urandom(16))))"

ZIGBEE2MQTT_NETWORK_KEY=[YOUR_16_INT_ARRAY_HERE]
ZIGBEE2MQTT_PAN_ID=YOUR_PAN_ID_HERE
ZIGBEE2MQTT_EXT_PAN_ID=[YOUR_8_INT_ARRAY_HERE]
```

> ⚠️ Replace the example values above with your own. Never commit real keys.
>
> If starting fresh, generate a new key and re-pair all Zigbee devices. If
> restoring from backup, use the original values from your secure backup.

### 4. Start services

```bash
docker compose up -d
```

Home Assistant will be available at `http://localhost:8123`.

### 5. Restore HA state (optional)

If you have a Home Assistant backup (.tar), restore it from:
**Settings → System → Backups → Restore**

> Databases, `.storage/`, integrations state, and entity registry are NOT in this repo — they live in HA backups.

### 6. Re-install custom components

Custom components (HACS integrations) are gitignored. After first boot:
1. Install HACS from the [official instructions](https://hacs.xyz/docs/use/download/download/)
2. Re-install: `dreame_vacuum`, `edata`, `meross_lan`, `meshtastic`, `moonraker`, `tapo_control`, `xiaomi_miot`, `llmvision`, `bluetti_bt`

## Custom Components

| Component | Purpose |
|---|---|
| `bluetti_bt` | Bluetti power station via Bluetooth |
| `dreame_vacuum` | Dreame/Xiaomi robot vacuum (X20) |
| `edata` | Spanish electricity consumption (PVPC) |
| `hacs` | Community Store |
| `meross_lan` | Meross smart plugs via LAN |
| `meshtastic` | LoRa mesh radio |
| `moonraker` | 3D printer (Ender 3 V3 SE) |
| `tapo_control` | TP-Link Tapo cameras (PTZ, snapshots) |
| `xiaomi_miot` | Xiaomi air purifier + vacuum |
| `llmvision` | LLM-powered camera analysis |

## CI / Validation

Every push to `main` runs three checks via GitHub Actions:

| Job | What it checks |
|---|---|
| **YAML Lint** | Syntax of all HA YAML files via `yamllint` |
| **Docker Compose Validate** | `docker compose config --quiet` |
| **HA Config Check** | `frenck/action-home-assistant` — integration and service validation |

Run locally before pushing:
```bash
pip install yamllint
yamllint -c .yamllint.yml homeassistant/configuration.yaml homeassistant/automations.yaml
docker compose config --quiet
```

## Open Issues

See [GitHub Issues](https://github.com/destaben/homeassistant/issues) for the full backlog. Priority items:

| # | Title | Priority |
|---|---|---|
| [#1](https://github.com/destaben/homeassistant/issues/1) | Zigbee network key in plaintext | ✅ Fixed — env vars |
| [#2](https://github.com/destaben/homeassistant/issues/2) | MQTT anonymous access | 🔴 High |
| [#3](https://github.com/destaben/homeassistant/issues/3) | nginx /auth/token blocks POST | 🟠 High |
| [#7](https://github.com/destaben/homeassistant/issues/7) | Replace manual MQTT lights with auto-discovery | 🟡 Medium |
| [#14](https://github.com/destaben/homeassistant/issues/14) | AI Vision epic | 🤖 Epic |
| [#15](https://github.com/destaben/homeassistant/issues/15) | Conversational AI epic | 🤖 Epic |
| [#16](https://github.com/destaben/homeassistant/issues/16) | Agentic AI ReAct loop epic | 🤖 Epic |

## Security Notes

- `secrets.yaml`, `.env`, `data/`, `etc_mosquitto/` are gitignored — never force-add them
- All credentials must use `!secret` references — never inline values
- MQTT currently allows anonymous connections ([#2](https://github.com/destaben/homeassistant/issues/2)) — fix before exposing externally
- HA container runs `privileged: true` ([#9](https://github.com/destaben/homeassistant/issues/9)) — reduce when integration compatibility allows

## Updating

```bash
git add homeassistant/automations.yaml homeassistant/configuration.yaml  # etc.
git commit -m "feat(automation): describe what changed"
git push
```

Only tracked config files sync. All runtime data is gitignored.
