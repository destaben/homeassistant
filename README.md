# Home Assistant - Disaster Recovery Configuration

Complete Home Assistant configuration for full disaster recovery and restoration.

## 📋 Repository Contents

### Main Files

- **`docker-compose.yaml`** - Service definitions (Home Assistant, Nginx, Cloudflared, Zigbee2MQTT, Mosquitto)
- **`nginx.conf`** - Reverse proxy configuration with endpoint filtering
- **`cloudflared/config.yml`** - Cloudflare tunnel configuration
- **`.env.example`** - Environment variables template
- **`.gitignore`** - Files to ignore (secrets, databases, logs)

### `homeassistant/` Directory

**Restorable Configuration:**
- `configuration.yaml` - Base configuration
- `automations.yaml` - Custom automations
- `scripts.yaml` - Custom scripts
- `scenes.yaml` - Scenes
- `ui-lovelace.yaml` - Custom dashboard
- `blueprints/` - Custom blueprints
- `custom_components/` - Installed components
- `www/` - Custom static files

**NOT included (auto-generated):**
- Databases (`*.db`, `*.db-wal`, `*.db-shm`)
- Logs (`home-assistant.log*`)
- Cache and system files (`.storage/`, `.cloud/`, `deps/`)
- Generated files (`media/`, `tts/`, `backups/`)

### `mosquitto_config/` Directory

- `mosquitto.conf` - MQTT configuration
- `mosquitto_certs.sh` - Certificate generation script

## 🚀 Full Restoration from Scratch

### 1. Clone the repository
```bash
git clone https://github.com/destaben/homeassistant.git
cd homeassistant
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your CLOUDFLARE_TUNNEL_TOKEN
```

### 3. Configure secrets (if any)
```bash
cp homeassistant/secrets.yaml.example homeassistant/secrets.yaml
# Edit and add your credentials
```

### 4. Update Cloudflare configuration
Edit `cloudflared/config.yml` and replace `homeassistant.tu-dominio.com` with your domain

### 5. Build and start containers
```bash
docker-compose up -d
```

### 6. Restore additional data (if exists)
If you have Home Assistant backups, restore from the interface:
1. Open `http://localhost:8123`
2. Settings → System → Backups → Restore

## 📁 Expected Directory Structure

```
/home/bmax/homeassistant/
├── docker-compose.yaml
├── nginx.conf
├── .env
├── .env.example
├── .gitignore
├── cloudflared/
│   └── config.yml
├── homeassistant/
│   ├── configuration.yaml
│   ├── automations.yaml
│   ├── scripts.yaml
│   ├── scenes.yaml
│   ├── secrets.yaml (⚠️ not versioned)
│   ├── ui-lovelace.yaml
│   ├── blueprints/
│   ├── custom_components/
│   └── www/
├── mosquitto_config/
│   ├── mosquitto.conf
│   └── mosquitto_certs.sh
└── README.md (this file)
```

## 🔐 Security

⚠️ **Important:**
- Never commit `secrets.yaml` to the repository
- Never commit `homeassistant/secrets.yaml`
- Use environment variables for credentials
- Repository must be **private**

## 📝 Notes

- Home Assistant databases will be created automatically on first run
- Mosquitto certificates will be generated automatically if they don't exist
- If using Zigbee2MQTT, configuration is in `docker-compose.yaml`
- Nginx proxy automatically filters to expose only necessary public endpoints

## 🔄 Updates

After any configuration changes:

```bash
git add .
git commit -m "Description of change"
git push
```

Only configuration files will be synced. Generated data is automatically ignored.

## ❓ Frequently Asked Questions

**Q: Why aren't backups included?**
A: Backups are large and unnecessary. They're protected within Home Assistant.

**Q: Will my connected devices be automatically restored?**
A: No. Some will require reconnection (Zigbee, Z-Wave, etc.). Secrets and credentials are required.

**Q: Can I use this on another machine?**
A: Yes, just change:
- IP in `nginx.conf` (if different)
- Variables in `.env`
- Domain in `cloudflared/config.yml`
