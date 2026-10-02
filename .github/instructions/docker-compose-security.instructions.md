---
name: Docker Compose Security Guidance
description: Safety guidance for changes to the Home Assistant Docker Compose stack.
applyTo: "docker-compose.yaml"
---

# Docker Compose Security

- Pin service image versions and preserve the existing restart policy conventions.
- Keep credentials and tokens in ignored environment files; never inline them in Compose.
- Treat host networking, exposed ports, device mounts, capabilities, and security options as security-sensitive changes requiring explicit justification.
- Preserve MQTT authentication and do not weaken network or container security merely to simplify connectivity.
- Run `docker compose config --quiet` after editing; do not start or restart services without explicit owner direction.