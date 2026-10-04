#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
deploy_root=${HOMEASSISTANT_DEPLOY_ROOT:-/opt/homeassistant}
compose_file="$deploy_root/compose.yaml"

for service in homeassistant zigbee2mqtt mosquitto; do
  [[ $(docker inspect --format '{{.State.Running}}' "$service") == "true" ]] || {
    printf 'ERROR: %s is not running\n' "$service" >&2
    exit 1
  }
done

[[ $(docker inspect --format '{{index .Config.Labels "com.docker.compose.project.config_files"}}' homeassistant) == "$compose_file" ]] || {
  printf 'ERROR: Home Assistant is not deployed from %s\n' "$deploy_root" >&2
  exit 1
}

ha_status=$(curl --retry 30 --retry-all-errors --retry-delay 1 --connect-timeout 5 --max-time 40 --silent --output /dev/null --write-out '%{http_code}' http://127.0.0.1:8123/api/ || true)
[[ "$ha_status" == "200" || "$ha_status" == "401" || "$ha_status" == "403" ]] || {
  printf 'ERROR: Home Assistant did not respond on port 8123 (HTTP %s)\n' "$ha_status" >&2
  exit 1
}

z2m_status=$(curl --retry 30 --retry-all-errors --retry-delay 1 --connect-timeout 5 --max-time 40 --silent --output /dev/null --write-out '%{http_code}' http://127.0.0.1:8082/ || true)
[[ "$z2m_status" =~ ^2[0-9]{2}$|^3[0-9]{2}$ ]] || {
  printf 'ERROR: Zigbee2MQTT did not respond on port 8082 (HTTP %s)\n' "$z2m_status" >&2
  exit 1
}

docker compose -f "$compose_file" ps
printf 'Container and HTTP verification passed. Verify MQTT clients and Home Assistant entities in the live UI before a production reload.\n'