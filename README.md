# Home Assistant Configuration

This repository contains configuration-as-code for a Home Assistant deployment using Docker Compose. It is not a complete backup of live Home Assistant state: integrations, registries, databases, credentials, and device state may require separate recovery sources.

## Services

The tracked [Compose file](docker-compose.yaml) defines these services:

| Service | Image | Configured ports / networking |
|---|---|---|
| Home Assistant | `ghcr.io/home-assistant/home-assistant:2026.9.4` | Host network mode |
| Zigbee2MQTT | `koenkk/zigbee2mqtt:2.8.0` | Host port `8082` maps to container port `8080` |
| Mosquitto | `eclipse-mosquitto:2.0` | Host port `1883`; bridge network |

nginx and Cloudflared are not defined in the tracked Compose file. Check the current [GitHub issue tracker](https://github.com/destaben/homeassistant/issues) for proposed work and status; issue state is not maintained in this README.

## Repository Guide

- [ha/configuration.yaml](ha/configuration.yaml) is the Home Assistant entry point and includes automations and scripts.
- [ha/automations.yaml](ha/automations.yaml), [ha/scripts.yaml](ha/scripts.yaml), and [ha/ui-lovelace.yaml](ha/ui-lovelace.yaml) hold automation, script, and YAML dashboard configuration.
- [ha/secrets.yaml.example](ha/secrets.yaml.example) contains secret-key names and placeholder values. Supply credentials locally, reference them with `!secret`, and never commit real values.
- [mosquitto/config/mosquitto.conf](mosquitto/config/mosquitto.conf) configures the broker to require a password file at `/etc/mosquitto/passwd`; Compose maps `mosquitto/certs/` to that container path.
- [AGENTS.md](AGENTS.md) defines shared AI operating rules. Copilot context and repository agents/instructions are under `.github/`.
- [`.github/agents/`](.github/agents/) contains focused workspace agents, [`.github/instructions/`](.github/instructions/) contains file-scoped guidance, and [`.github/skills/`](.github/skills/) contains reusable workflows. Use the Documentation Steward and AI Context Audit when reviewing repository documentation or AI context.
- [`.github/prompts/`](.github/prompts/) contains entry points for automation delivery, presence design, security review, Assist/voice capability, dashboard work, and full repository reviews. The specialist tooling changes tracked files only after source verification and never deploys or performs live Home Assistant actions.
- The [Home Operations Diagnostician](.github/agents/home-operations-diagnostician.agent.md) investigates events and failures using bounded, read-only live Docker diagnostics. It may inspect operational evidence needed for a specific question, but cannot control devices, call services, restart or deploy containers, or inspect secrets.
- Use the [AI Vision Roadmap skill](.github/skills/ai-vision-roadmap/SKILL.md) for camera analysis, privacy constraints, and vision-driven automation planning.

The Zigbee2MQTT data directory and live Home Assistant state are deployment data, not sources for repository documentation. Preserve them separately when planning a migration or disaster-recovery procedure. Do not infer their current contents or availability from this repository.

## Dashboard Conventions

The YAML dashboard uses one sections-based Casa view organized by room. Keep room controls compact and use familiar Material Design icons; presence and occupancy indicators use `mdi:motion-sensor` consistently. Controls that change a device state use a direct toggle only when the effect is clear, while sensors and navigation targets open their details with `more-info`.

For the vacuum, the **Estancias** control opens the native area selector and **Casa completa** runs the tracked script that starts a whole-home clean or sends an active vacuum back to its base. Camera controls belong with their rooms: the `mdi:cctv` buttons open a Browser Mod popup with the stream under demand. Preserve these explicit labels and actions when changing the dashboard.

Browser Mod is installed locally as a custom integration through HACS or `ha/custom_components/browser_mod/`, which is intentionally ignored by Git. After installing or updating it, restart Home Assistant, add **Browser Mod** in **Settings → Devices & Services**, restart once more, and register the browser in its Browser Mod panel before testing camera popups. This runtime setup is not established by the tracked YAML alone.

## Validation

The tracked [GitHub Actions workflow](.github/workflows/validate.yml) runs YAML linting, Docker Compose validation, and a Home Assistant configuration check. The Home Assistant check is explicitly allowed to fail because device-registry references may not resolve outside the live instance; treat it as advisory, not as a passing guarantee. Pull-request runs are path-filtered to HA YAML and `docker-compose.yaml`; pushes to `main` or `master` trigger the workflow.

Run the checks locally from the repository root:

On this host, run Docker commands as a user in the `docker` group with `docker context show` set to `default`.

```bash
pip install yamllint
yamllint -c .yamllint.yml \
  ha/configuration.yaml ha/automations.yaml ha/scripts.yaml \
  ha/scenes.yaml ha/ui-lovelace.yaml
docker compose config --quiet
```

For HA-specific validation, also use **Developer Tools → YAML → Check configuration** in the target Home Assistant instance before restarting or reloading a production system. That live check cannot be run from this documentation review.

## Clean Host Recovery and Operation

The supported recovery layout uses one checkout at `/opt/homeassistant`. Clone the
approved revision there, restore the ignored runtime directories and secret
material from approved encrypted backups, then validate and start Compose from
that same checkout. Do not use a separate source checkout or copy the Compose
file into a second runtime directory.

```bash
git clone https://github.com/destaben/homeassistant.git /opt/homeassistant
cd /opt/homeassistant
# Restore the approved private runtime material before continuing.
pip install yamllint
yamllint -c .yamllint.yml \
  ha/configuration.yaml ha/automations.yaml ha/scripts.yaml \
  ha/scenes.yaml ha/ui-lovelace.yaml
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps
```

Run these commands only on a replacement host after the recovery procedure has
verified the coordinator and network cutover. Never start a second Home
Assistant or Zigbee2MQTT instance against the production coordinator or Zigbee
network.

For a normal configuration update, review the change in the same checkout, run
the validation commands above, then use `docker compose pull` and `docker
compose up -d`. To use an earlier tracked configuration, check out the approved
Git revision in a clean worktree and repeat the validation and Compose commands.
Neither approach restores runtime data; use the recovery runbook when data must
be restored.

## Credentials and Recovery

- Keep credentials, MQTT password files, Zigbee network keys, and generated deployment state out of tracked files.
- Use Home Assistant `!secret` references and placeholder-only examples.
- The broker configuration disables anonymous access. Create its password file before starting the broker and configure clients with matching credentials; never put the passwords in this README or Compose file.
- Follow the [disaster-recovery runbook](docs/disaster-recovery.md) to back up and restore the untracked deployment data. This repository alone is not a complete recovery source.

For current incidents, priorities, and feature requests, consult the [GitHub Issues](https://github.com/destaben/homeassistant/issues) page directly.
