# Wake-on-LAN for closed-lid MacBooks

Home Assistant sends a magic packet through `switch.*_wol` entities defined in
[ha/configuration.yaml](../ha/configuration.yaml). The container uses host networking, so the
broadcast reaches the LAN directly. Targets must be on the same subnet and connected by
Ethernet and mains power. Wake works from sleep only, not from a full shutdown.

Real values go in the untracked `ha/secrets.yaml`; see
[ha/secrets.yaml.example](../ha/secrets.yaml.example) for the key names.

## Get the MAC address (Ethernet interface only, not Wi-Fi)

- **macOS (Air, Neo):** plug in the Ethernet adapter, then run `networksetup -listallhardwareports`
  and use the `Ethernet Address` of the adapter's port. Or: System Settings → Network → the
  Ethernet adapter → Details → Hardware.

Also reserve a fixed IP for each MAC in the router (DHCP reservation); it is used for the ping state.

## Per-device setup

### macOS (Apple Silicon)
1. System Settings → Battery → Options → enable **Wake for network access** (power adapter).
2. `sudo pmset -a womp 1`, then confirm with `pmset -g | grep womp`.
3. Keep the Mac on its charger, Ethernet attached, and let it sleep with the lid closed.

Limitation: a sleeping Mac may still answer ping through the network sleep proxy, so the ping-based
state can read "on" while asleep. Verify behaviour per device.

## Rollout state
Only the `MacBook Neo WoL` switch is active. The Neo and the Air currently share one USB-LAN
adapter, so the switch targets the adapter's MAC and its reserved IP (`.60`) and wakes whichever Mac has
the adapter plugged in. The Air switch stays commented out in `ha/configuration.yaml`: uncomment it
after the Air gets its own adapter and its `wol_macbook_air_*` keys are in `ha/secrets.yaml` (an
undefined `!secret` makes the whole configuration invalid). Give each adapter a DHCP reservation in the
router so the ping state stays valid.

## Validation
After filling `ha/secrets.yaml`, run Developer Tools → YAML → Check configuration, restart Home
Assistant, then call `switch.turn_on` on each WoL entity while that laptop is asleep.
