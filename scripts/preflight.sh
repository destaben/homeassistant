#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
deploy_root=${HOMEASSISTANT_DEPLOY_ROOT:-/opt/homeassistant}
source_compose="$repo_root/docker-compose.yaml"
deploy_compose="$deploy_root/compose.yaml"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_path() {
  [[ -e "$1" ]] || fail "required path is unavailable: $1"
}

[[ -f "$source_compose" ]] || fail "Compose file not found: $source_compose"

docker compose -f "$source_compose" config --quiet
require_path /run/dbus
require_path /run/udev
require_path /dev/ttyUSB0
require_path /dev/serial/by-id/usb-ITead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_fc0671e16fbeed119095a04838a92db5-if00-port0
require_path "$repo_root/ha"
require_path "$repo_root/zigbee2mqtt"
require_path "$repo_root/mosquitto/certs"
require_path "$repo_root/mosquitto/config"

active_project=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' homeassistant 2>/dev/null || true)
[[ "$active_project" == "homeassistant" ]] || fail "the active Home Assistant container is not owned by this Compose project"

active_config=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project.config_files"}}' homeassistant)
case "$active_config" in
  "$source_compose") printf 'Preflight passed. Home Assistant still runs from the source directory.\n' ;;
  "$deploy_compose")
    docker compose -f "$deploy_compose" config --quiet
    require_path "$deploy_root/ha"
    require_path "$deploy_root/zigbee2mqtt"
    require_path "$deploy_root/mosquitto/certs"
    require_path "$deploy_root/mosquitto/config"
    printf 'Preflight passed. Home Assistant runs from %s.\n' "$deploy_root"
    ;;
  *) fail "the active Home Assistant container uses $active_config, not a managed Compose file" ;;
esac

printf 'No services were changed.\n'