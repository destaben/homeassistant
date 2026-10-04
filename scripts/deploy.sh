#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
deploy_root=${HOMEASSISTANT_DEPLOY_ROOT:-/opt/homeassistant}
compose_file="$deploy_root/compose.yaml"
services=("$@")

if ((${#services[@]} == 0)); then
  services=(homeassistant zigbee2mqtt mosquitto)
fi

for service in "${services[@]}"; do
  case "$service" in
    homeassistant|zigbee2mqtt|mosquitto) ;;
    *) printf 'ERROR: unsupported service: %s\n' "$service" >&2; exit 2 ;;
  esac
done

"$repo_root/scripts/preflight.sh"
active_config=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project.config_files"}}' homeassistant)
[[ "$active_config" == "$compose_file" ]] || {
  printf 'ERROR: Home Assistant has not been cut over to %s\n' "$deploy_root" >&2
  exit 1
}
install -m 0644 "$repo_root/docker-compose.yaml" "$compose_file"
docker compose -f "$compose_file" pull "${services[@]}"
docker compose -f "$compose_file" up -d --no-deps "${services[@]}"
docker compose -f "$compose_file" ps "${services[@]}"