# Home Configuration Map

This is a functional map of the tracked Home Assistant configuration. It helps
AI assistants reason about intended behavior before proposing changes. It is not
an inventory of live devices, entity registry data, states, events, presence,
or recorder history.

## Scope and Sources

The authoritative sources are the tracked files named in each section. An
entity reference means that the configuration expects the entity to exist; it
does not prove current availability, ownership, location, state, or history.
Never add credentials, network addresses, registry identifiers, live states,
event payloads, or recorder extracts to this document.

Use the Home Operations Diagnostician for a specific, bounded, read-only live
question. Treat its findings as transient diagnostic evidence, not repository
documentation. Update this map only when its tracked sources change.

## Configuration Entry Points

[`ha/configuration.yaml`](../ha/configuration.yaml) is the Home Assistant entry
point. It includes [`ha/automations.yaml`](../ha/automations.yaml) and
[`ha/scripts.yaml`](../ha/scripts.yaml), declares the YAML-mode dashboard, and
defines these configuration-owned capabilities:

- Five `input_text` helpers retain sanitized recent public Meshtastic activity.
- Derivative and statistics sensors summarize configured Meshtastic counters.
- Seven MQTT switches implement the numbered lighting endpoints.
- Recorder, history, logbook, API, and Assist pipeline support are enabled.
- A snapshot-retention shell command removes old alarm snapshots.

[`ha/scenes.yaml`](../ha/scenes.yaml) is currently empty. Do not propose scene
changes as though a configured scene catalog exists.

## Functional Entity Groups

### Lighting and Local Controls

Source: [`ha/automations.yaml`](../ha/automations.yaml),
[`ha/configuration.yaml`](../ha/configuration.yaml), and
[`ha/ui-lovelace.yaml`](../ha/ui-lovelace.yaml).

- The numbered MQTT switches are individual lighting endpoints. `switch.light`
  is intentionally used as a group control in configured flows; do not assume
  it is interchangeable with a single numbered endpoint.
- Two Zigbee2MQTT button action topics accept `single`, `double`, and `hold`
  payloads. Existing actions control lighting, plugs, and alarm enablement.
- Entry contact and entry occupancy flows turn on selected lights. The entry
  close flow handles delayed group shutdown and camera preset selection.
- The dashboard exposes room-oriented direct controls and occupancy/contact
  details. Preserve the existing distinction between a direct toggle and a
  `more-info` action.

### Access, Presence, and Alarm

Source: [`ha/automations.yaml`](../ha/automations.yaml).

- Two configured person entities drive home-empty shutdown and return-home
  alarm disarm behavior. They are safety-sensitive dependencies, not a
  substitute for a verified occupancy model.
- Door and window contacts participate in entry behavior, alarm activation,
  and the nighttime arming precondition.
- The alarm automation can capture a camera snapshot, issue local media alerts,
  send mobile notifications, and apply a cooldown. It also has explicit enable
  and disable announcements.
- Night arming requires both configured phone-battery signals, both configured
  people at home, the alarm disabled, and all tracked contacts closed. If a
  contact is open or unavailable, it announces the reason rather than arming.

Changes involving people, doors, windows, cameras, alarms, push notifications,
or MQTT exposure require a Home Security Reviewer assessment before editing.

### Comfort, Appliances, and Cleaning

Source: [`ha/automations.yaml`](../ha/automations.yaml),
[`ha/scripts.yaml`](../ha/scripts.yaml), and
[`ha/ui-lovelace.yaml`](../ha/ui-lovelace.yaml).

- The air purifier has scheduled `Auto` and `Sleep` preset actions.
- A configured plug is scheduled as a heater control. Do not replace its fixed
  schedule with temperature-based logic without a tracked, verified sensor and
  a safety review of the connected load.
- Another configured plug and room controls are exposed in the dashboard; use
  the configured aliases and ownership rather than inferring appliance purpose
  from an entity identifier.
- Daily cleaning uses the configured vacuum and purifier. The
  `vacuum_clean_all_or_return` script starts cleaning when idle or returns an
  active vacuum to base.
- Low water and low battery conditions send configured mobile notifications.
  The low-battery scan applies to sensor entity IDs containing `battery` and
  reports values below five percent.

### Cameras and Media

Source: [`ha/automations.yaml`](../ha/automations.yaml),
[`ha/scripts.yaml`](../ha/scripts.yaml), and
[`ha/ui-lovelace.yaml`](../ha/ui-lovelace.yaml).

- Camera preset scripts select the configured entry or living-area presets.
- Motion, door, departure, and alarm flows can select a camera preset.
- Dashboard camera popups display streams on demand and expose the two preset
  scripts where configured.
- Media players provide alarm tones and announcements. Avoid changing volume or
  playback behavior without considering the alarm path.

Camera availability and camera endpoint details are live deployment facts. Do
not record them here or treat a diagnostic failure as a configuration defect.

### Meshtastic

Source: [`ha/configuration.yaml`](../ha/configuration.yaml) and
[`ha/automations.yaml`](../ha/automations.yaml).

- Recent public activity is shifted through five helpers after a configured
  Meshtastic event passes channel, sender-availability, and non-empty-message
  checks. Stored messages are length-limited and sanitized into JSON.
- The broadcast event delegates to a dedicated queued script. That script
  accepts a non-empty message of up to 240 characters, uses the configured
  channel, and requests no acknowledgement.
- Derived rates and one-hour statistics support observability of configured
  Meshtastic counters. They are not evidence of current network health.

Preserve message validation, fixed-channel routing, and bounded helper storage
when changing these flows.

## MQTT Contract

Source: [`ha/configuration.yaml`](../ha/configuration.yaml),
[`ha/automations.yaml`](../ha/automations.yaml), and
[`mosquitto/config/mosquitto.conf`](../mosquitto/config/mosquitto.conf).

- Each numbered MQTT light uses matching Zigbee2MQTT state and command topics.
  Its command payload is JSON with an `ON` or `OFF` state; state parsing reads
  the JSON `state` property. The switches use QoS 1 and retained state.
- Button automations consume Zigbee2MQTT action topics, not Home Assistant
  device triggers. Preserve the payload contract when changing button behavior.
- Mosquitto listens on its configured listener, disables anonymous access, and
  requires a password file. Never document, inspect, or add credential values.

## Dashboard Workflows

Source: [`ha/ui-lovelace.yaml`](../ha/ui-lovelace.yaml).

The single YAML-mode Home view is organized into a status overview and room
sections. It provides:

- environmental and smoke status indicators;
- person, alarm, and cleaning status tiles;
- direct room controls for lights, plugs, purifier, remotes, and media;
- detail views for occupancy and contact sensors; and
- on-demand camera popups with configured camera-preset actions.

Keep this room-oriented navigation and the explicit control semantics when
editing the dashboard. Use the Lovelace Dashboard Engineer for dashboard work.

## Change Routing

- Automations, scripts, core configuration, and MQTT definitions: Home
  Assistant Engineer, after verifying every referenced entity in tracked files.
- Alarms, access, cameras, presence, notifications, and MQTT security: Home
  Security Reviewer before implementation.
- Presence or occupancy design: Presence Intelligence Planner.
- Assist or voice behavior: Assist Experience Designer.
- Dashboard behavior: Lovelace Dashboard Engineer.
- Recorder, runtime events, availability, or container incidents: Home
  Operations Diagnostician, using the bounded read-only diagnostic exception.

Validate tracked configuration changes with the `ha-validation` skill. Do not
restart, reload, deploy, or call Home Assistant services unless explicitly
requested.