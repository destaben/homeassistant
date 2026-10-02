---
name: ha-validation
description: "Validate tracked Home Assistant and Docker Compose configuration changes. Use after editing Home Assistant YAML, Mosquitto configuration, or docker-compose.yaml."
argument-hint: "List the changed configuration files and the validation you need."
user-invocable: true
---

# Home Assistant Validation

## Procedure

1. Run `git diff --check`.
2. For Home Assistant YAML, run the repository `yamllint` command over all configured HA YAML files.
3. For Compose changes, run `docker compose config --quiet` without exposing `.env` values.
4. For production-bound Home Assistant changes, require **Developer Tools → YAML → Check configuration** before reload or restart.
5. Record which checks were run, skipped, or unavailable. YAML validity alone does not prove live entities or devices resolve.

## Boundary

Never restart containers, reload Home Assistant, or perform live service actions as part of validation unless the owner explicitly requests it.