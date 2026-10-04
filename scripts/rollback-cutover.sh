#!/usr/bin/env bash
set -euo pipefail

[[ $# -eq 1 && "$1" == "--confirm" ]] || { printf 'Usage: %s --confirm\n' "$0" >&2; exit 2; }
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
deploy_root=${HOMEASSISTANT_DEPLOY_ROOT:-/opt/homeassistant}
backup_root=/opt/migration-backups/rollback-homeassistant-$(date +%F-%H%M%S)

sudo install -d -m 0700 "$backup_root"
sudo docker compose -f "$deploy_root/compose.yaml" stop
sudo tar --xattrs --acls -C "$deploy_root" -czf "$backup_root/runtime-before-rollback.tgz" ha zigbee2mqtt mosquitto
sudo rsync -aHAX --delete "$deploy_root/ha/" "$repo_root/ha/"
sudo rsync -aHAX --delete "$deploy_root/zigbee2mqtt/" "$repo_root/zigbee2mqtt/"
sudo rsync -aHAX --delete "$deploy_root/mosquitto/" "$repo_root/mosquitto/"
sudo docker compose -f "$deploy_root/compose.yaml" rm -f
sudo docker compose -f "$repo_root/docker-compose.yaml" up -d
printf 'Restored Home Assistant source deployment. Backup: %s\n' "$backup_root"