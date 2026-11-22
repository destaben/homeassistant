# Wake-on-LAN for closed-lid laptops

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
- **Windows (ASUS FX505):** `ipconfig /all` in a terminal; use "Physical Address" of the
  "Ethernet adapter" section (Realtek PCIe GbE).

Also reserve a fixed IP for each MAC in the router (DHCP reservation); it is used for the ping state.

## Per-device setup

### macOS (Apple Silicon)
1. System Settings → Battery → Options → enable **Wake for network access** (power adapter).
2. `sudo pmset -a womp 1`, then confirm with `pmset -g | grep womp`.
3. Keep the Mac on its charger, Ethernet attached, and let it sleep with the lid closed.

Limitation: a sleeping Mac may still answer ping through the network sleep proxy, so the ping-based
state can read "on" while asleep. Verify behaviour per device.

### ASUS FX505 (Windows)
1. BIOS (F2): enable "Power On By PCI-E" / Wake on LAN if present.
2. Device Manager → Realtek adapter → Advanced: "Wake on Magic Packet" = Enabled; Power
   Management: allow the device to wake the computer, magic packet only.
3. Control Panel → Power Options → disable **Fast startup**.
4. Lid close action: Sleep (or Do nothing).

## Rollout state
Only the MacBook Neo switch is active. The Air and ASUS switches are commented out in
`ha/configuration.yaml` because their Ethernet MAC/IP are not known yet; uncomment them after
adding their `wol_*` keys to `ha/secrets.yaml` (an undefined `!secret` makes the whole
configuration invalid). Give each laptop a DHCP reservation in the router so the ping state stays valid.

## Validation
After filling `ha/secrets.yaml`, run Developer Tools → YAML → Check configuration, restart Home
Assistant, then call `switch.turn_on` on each WoL entity while that laptop is asleep.
