#!/usr/bin/env bash
set -euo pipefail

[[ $# -eq 2 && "$1" == "--confirm" ]] || {
  printf 'Usage: %s --confirm <git-ref>\n' "$0" >&2
  exit 2
}

target_ref=$2
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

git diff --quiet || {
  printf 'ERROR: working tree has changes; commit or stash them before rollback\n' >&2
  exit 1
}
git rev-parse --verify --quiet "$target_ref^{commit}" >/dev/null || {
  printf 'ERROR: unknown Git reference: %s\n' "$target_ref" >&2
  exit 1
}

git switch --detach "$target_ref"
"$repo_root/scripts/deploy.sh"
"$repo_root/scripts/verify.sh"
printf 'Rolled back deployment configuration to %s. Persistent data was not modified.\n' "$target_ref"