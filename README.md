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
- Use the [AI Vision Roadmap skill](.github/skills/ai-vision-roadmap/SKILL.md) for camera analysis, privacy constraints, and vision-driven automation planning.

The Zigbee2MQTT data directory and live Home Assistant state are deployment data, not sources for repository documentation. Preserve them separately when planning a migration or disaster-recovery procedure. Do not infer their current contents or availability from this repository.

## Validation

The tracked [GitHub Actions workflow](.github/workflows/validate.yml) runs YAML linting, Docker Compose validation, and a Home Assistant configuration check. The Home Assistant check is explicitly allowed to fail because device-registry references may not resolve outside the live instance; treat it as advisory, not as a passing guarantee. Pull-request runs are path-filtered to HA YAML and `docker-compose.yaml`; pushes to `main` or `master` trigger the workflow.

Run the checks locally from the repository root:

Docker commands on this host require `sudo`.

```bash
pip install yamllint
yamllint -c .yamllint.yml \
  ha/configuration.yaml ha/automations.yaml ha/scripts.yaml \
  ha/scenes.yaml ha/ui-lovelace.yaml
sudo docker compose config --quiet
```

For HA-specific validation, also use **Developer Tools → YAML → Check configuration** in the target Home Assistant instance before restarting or reloading a production system. That live check cannot be run from this documentation review.

## Credentials and Recovery

- Keep credentials, MQTT password files, Zigbee network keys, and generated deployment state out of tracked files.
- Use Home Assistant `!secret` references and placeholder-only examples.
- The broker configuration disables anonymous access. Create its password file before starting the broker and configure clients with matching credentials; never put the passwords in this README or Compose file.
- Back up Home Assistant state and Zigbee2MQTT data separately using a secure process appropriate to the deployment. This repository alone does not establish a complete restore procedure.

For current incidents, priorities, and feature requests, consult the [GitHub Issues](https://github.com/destaben/homeassistant/issues) page directly.
