# Home Assistant — Configuration as Code

Self-hosted smart home running on Docker Compose. This repository is a full disaster-recovery snapshot of all configuration.

## Stack

| Service | Image | Role |
|---|---|---|
| Home Assistant | `ghcr.io/home-assistant/home-assistant:2026.9.4` | Core platform |
| Zigbee2MQTT | `koenkk/zigbee2mqtt:2.8.0` | Zigbee coordinator (Sonoff 3.0 USB) |
| Mosquitto | `eclipse-mosquitto:2.0` | MQTT broker |
| nginx | `nginx:stable` | Security reverse proxy for Google Assistant OAuth *(not yet added)* |
| Cloudflared | `cloudflare/cloudflared` | External tunnel via `hassistant.destaben.dev` *(not yet added)* |

> nginx and cloudflared are not yet added to `docker-compose.yaml`. See [#5](https://github.com/destaben/homeassistant/issues/5) to add and enable them.

## Repository Layout

```
ha/                         # HA config (bind-mounted to /config in container)
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

zigbee2mqtt/                # ⚠️ NOT versioned — Zigbee2MQTT state + network key
mosquitto/
  config/                   # Mosquitto static config (versioned)
    mosquitto.conf
    mosquitto_certs.sh
  certs/                    # ⚠️ NOT versioned — runtime certs/passwd
docker-compose.yaml         # All service definitions (versioned)
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
cp ha/secrets.yaml.example ha/secrets.yaml
# Edit secrets.yaml — add all credentials
```

### 2a. Create MQTT password file

The Mosquitto broker requires a password file at `./mosquitto/certs/passwd` (mapped to
`/etc/mosquitto/passwd` inside the container).  Run these commands **after** the
containers have started at least once (so the image is available), or run them
independently against the Mosquitto image:

```bash
sudo mkdir -p mosquitto/certs

# Create the password file with the homeassistant user (-c creates a new file)
sudo docker run --rm -v "$(pwd)/mosquitto/certs:/etc/mosquitto" \
  eclipse-mosquitto:2.0 \
  mosquitto_passwd -c -b /etc/mosquitto/passwd homeassistant YOUR_HA_MQTT_PASSWORD

# Add the zigbee2mqtt user
sudo docker run --rm -v "$(pwd)/mosquitto/certs:/etc/mosquitto" \
  eclipse-mosquitto:2.0 \
  mosquitto_passwd -b /etc/mosquitto/passwd zigbee2mqtt YOUR_Z2M_MQTT_PASSWORD
```

Set the Zigbee2MQTT password in `zigbee2mqtt/configuration.yaml` under `mqtt.password`.
Configure Home Assistant separately in **Settings → Devices & services → MQTT →
Reconfigure** using host `localhost`, port `1883`, user `homeassistant`, and the
matching password. MQTT connection credentials are managed by the Home Assistant
MQTT integration, not by `configuration.yaml`.

> ⚠️ `zigbee2mqtt/configuration.yaml` is gitignored because it also contains the Zigbee
> network key — edit it carefully and keep it in a secure offline backup.

### 3. Restore Zigbee2MQTT config

`zigbee2mqtt/` is gitignored because it contains the Zigbee network key. You need to either:
- Restore `zigbee2mqtt/configuration.yaml` from a secure backup, **or**
- Re-pair all Zigbee devices via the Zigbee2MQTT dashboard after first boot

### 4. Migrate an existing deployment

Stop the stack and back up the existing state before starting the updated Compose configuration. The target paths must not already contain runtime state.

```bash
sudo docker compose down
backup_dir="../homeassistant-layout-backup-$(date +%Y%m%d-%H%M%S)"
sudo mkdir "$backup_dir"
sudo cp -a homeassistant data etc_mosquitto "$backup_dir/"

sudo test ! -e ha/.storage
sudo test ! -e zigbee2mqtt
sudo test ! -e mosquitto/certs
sudo cp -a homeassistant/. ha/
sudo mv data zigbee2mqtt
sudo mkdir -p mosquitto
sudo mv etc_mosquitto mosquitto/certs
```

This preserves Home Assistant's `.storage`, secrets, custom components, databases, and backups. `zigbee2mqtt/` contains the Zigbee network key and `mosquitto/certs/` may contain the MQTT password file.

### 5. Start services

```bash
sudo docker compose up -d
sudo docker compose ps
```

Home Assistant will be available at `http://localhost:8123`. Confirm all services are healthy and the existing Home Assistant instance loads before deleting `homeassistant/`, `data/`, or `etc_mosquitto/`; the backup directory is the recovery point.

### 6. Restore HA state (optional)

If you have a Home Assistant backup (.tar), restore it from:
**Settings → System → Backups → Restore**

> Databases, `.storage/`, integrations state, and entity registry are NOT in this repo — they live in HA backups.

### 7. Re-install custom components

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
yamllint -c .yamllint.yml ha/configuration.yaml ha/automations.yaml
docker compose config --quiet
```

## Open Issues

See [GitHub Issues](https://github.com/destaben/homeassistant/issues) for the full backlog. Priority items:

| # | Title | Priority |
|---|---|---|
| [#1](https://github.com/destaben/homeassistant/issues/1) | Zigbee network key in plaintext | 🔴 Critical |
| [#2](https://github.com/destaben/homeassistant/issues/2) | MQTT anonymous access | ✅ Fixed |
| [#3](https://github.com/destaben/homeassistant/issues/3) | nginx /auth/token blocks POST | 🟠 High |
| [#7](https://github.com/destaben/homeassistant/issues/7) | Replace manual MQTT lights with auto-discovery | 🟡 Medium |
| [#14](https://github.com/destaben/homeassistant/issues/14) | AI Vision epic | 🤖 Epic |
| [#15](https://github.com/destaben/homeassistant/issues/15) | Conversational AI epic | 🤖 Epic |
| [#16](https://github.com/destaben/homeassistant/issues/16) | Agentic AI ReAct loop epic | 🤖 Epic |
| [#17](https://github.com/destaben/homeassistant/issues/17) | Predictive ML automation epic | 🤖 Epic |

## Security Notes

- `secrets.yaml`, `.env`, `zigbee2mqtt/`, `mosquitto/certs/` are gitignored — never force-add them
- All credentials must use `!secret` references — never inline values
- MQTT anonymous access is disabled; create `mosquitto/certs/passwd` as described above before starting the broker
- HA container runs `privileged: true` ([#9](https://github.com/destaben/homeassistant/issues/9)) — reduce when integration compatibility allows

## Updating

```bash
git add ha/automations.yaml ha/configuration.yaml  # etc.
git commit -m "feat(automation): describe what changed"
git push
```

Only tracked config files sync. All runtime data is gitignored.
