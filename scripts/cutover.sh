#!/usr/bin/env bash
set -euo pipefail

[[ $# -eq 1 && "$1" == "--confirm" ]] || {
  printf 'Usage: %s --confirm\n' "$0" >&2
  exit 2
}

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
deploy_root=${HOMEASSISTANT_DEPLOY_ROOT:-/opt/homeassistant}
source_compose="$repo_root/docker-compose.yaml"
deploy_compose="$deploy_root/compose.yaml"
backup_root=${HOMEASSISTANT_BACKUP_ROOT:-/opt/migration-backups/$(date +%F-%H%M%S)}

"$repo_root/scripts/preflight.sh"
[[ $(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project.config_files"}}' homeassistant) == "$source_compose" ]] || {
  printf 'ERROR: cutover requires the source deployment to be active\n' >&2
  exit 1
}

sudo install -d -m 0750 "$deploy_root" "$backup_root"
sudo tar --xattrs --acls -C "$repo_root" -czf "$backup_root/homeassistant-runtime.tgz" ha zigbee2mqtt mosquitto

rollback_source() {
  sudo docker compose -f "$deploy_compose" rm -sf homeassistant zigbee2mqtt mosquitto || true
  sudo docker compose -f "$source_compose" up -d || true
}
trap rollback_source ERR

sudo docker compose -f "$source_compose" stop
sudo rsync -aHAX --delete "$repo_root/ha/" "$deploy_root/ha/"
sudo rsync -aHAX --delete "$repo_root/zigbee2mqtt/" "$deploy_root/zigbee2mqtt/"
sudo rsync -aHAX --delete "$repo_root/mosquitto/" "$deploy_root/mosquitto/"
sudo install -m 0644 "$source_compose" "$deploy_compose"
sudo docker compose -f "$source_compose" rm -f
sudo docker compose -f "$deploy_compose" config --quiet
sudo docker compose -f "$deploy_compose" up -d
trap - ERR
"$repo_root/scripts/verify.sh"
printf 'Home Assistant cutover completed. Backup: %s\n' "$backup_root"