# Disaster Recovery Runbook

This runbook describes how to rebuild the tracked deployment after a host loss. It does not replace encrypted, access-controlled backups of untracked data. Test the procedure in an isolated environment at least once after material changes.

## Recovery Scope

The Git repository restores the tracked Compose, Home Assistant, Mosquitto, and dashboard configuration. A complete recovery also requires secure backups of the following untracked data:

- Home Assistant runtime state needed by the deployment, including integration and entity registries, custom integrations, frontend resources, and media required by automations.
- Zigbee2MQTT data, including its configuration, coordinator backup, network key, and state.
- Home Assistant secrets and Mosquitto password material.
- The version, source, and setup record for locally installed HACS integrations, including Browser Mod.

Never store these backup contents or credential values in Git. Keep encrypted off-host copies and record their location, owner, retention period, and last successful restore test outside this repository.

## Host Preconditions

Before restoring, verify the replacement host has Docker Engine and Docker Compose, the correct timezone, and access to the required network.

Check the device paths in [docker-compose.yaml](../docker-compose.yaml) before starting services. The tracked configuration references `/dev/ttyUSB0`, a specific Zigbee USB adapter path under `/dev/serial/by-id/`, `/run/dbus`, and `/run/udev`. Replacement hardware may use different paths.

Do not run a restore host against the production Zigbee coordinator or network until the recovery plan explicitly calls for cutover. Two active services using the same coordinator or Zigbee network can cause data loss or device instability.

## Restore Procedure

1. Clone this repository at the intended revision and create a working copy of the ignored deployment directories from the approved encrypted backup source.
2. Restore Home Assistant runtime data, Zigbee2MQTT data, and Mosquitto password material with their original ownership and permissions. Use [ha/secrets.yaml.example](../ha/secrets.yaml.example) only as a list of secret-key names; obtain values from the approved secret store.
3. Confirm the Mosquitto password file exists at the host path mounted as `/etc/mosquitto/passwd`. Keep anonymous access disabled.
4. Confirm the Home Assistant, Zigbee2MQTT, and Mosquitto mount paths in [docker-compose.yaml](../docker-compose.yaml) exist. Adjust only verified replacement-hardware paths; do not add credentials to Compose.
5. Run the tracked validation commands:

   ```bash
   pip install yamllint
   yamllint -c .yamllint.yml \
     ha/configuration.yaml ha/automations.yaml ha/scripts.yaml \
     ha/scenes.yaml ha/ui-lovelace.yaml
   docker compose config --quiet
   ```

6. Start the services using the approved operational change process. Do not start or restart the production deployment merely to test this document.
7. In Home Assistant, run **Developer Tools → YAML → Check configuration** before any production reload or restart.
8. Restore and configure Browser Mod if camera popups are required: install the approved version, add the integration, restart through the approved process, and register each browser. The dashboard uses Browser Mod at runtime but it is intentionally not tracked.

## Post-Restore Verification

Verify these outcomes in the restored environment before treating it as ready:

- Mosquitto rejects anonymous access and Home Assistant and Zigbee2MQTT connect with their restored credentials.
- The Zigbee coordinator is detected at the verified path and expected devices are available.
- Home Assistant resolves the entities referenced by the dashboard, automations, scripts, and TTS announcements.
- The alarm starts disabled until an owner confirms the current door/window contacts, presence states, and phone charging states.
- Camera popups, snapshot storage cleanup, alarm notifications, and TTS announcements work as intended.

Record the restore date, configuration revision, backup revision, failures, and follow-up work in the operational record. A successful YAML or Compose validation does not prove live hardware, credentials, integrations, or entity registries were restored correctly.

## Live-Verified Security Decisions

The tracked configuration intentionally leaves these decisions pending a live verification. Record the approved outcome and test it after recovery:

- Restrict Mosquitto and Zigbee2MQTT port bindings only after identifying every required LAN client and administration path.
- Verify whether Home Assistant still needs host networking, `NET_ADMIN`, `NET_RAW`, and an unconfined AppArmor profile before removing any of them.
- Confirm the intended alarm policy for presence-based disarming and manual overrides. The nighttime routine fails closed when a monitored door or window is open or unavailable.
- Verify the configured TTS provider and both speaker entities with a live announcement test. The provider and integration setup are runtime state, not tracked YAML.