# ICP Automatic Re-arm Design

This record covers re-arming the ICP (power-control switch) through the distributor's private web area after a trip, instead of doing it by hand. It documents decisions and constraints only. No tracked Home Assistant configuration, Compose service, or script implements it yet, and nothing here has been run against a real distributor account. Anything marked **unverified** must be checked on the live system before it is relied on.

## Scope

- The re-arm tooling is an unofficial client ([`trocotronic/edistribucion`](https://github.com/trocotronic/edistribucion)) wrapped by two scripts, run on the host chosen under the host options below (the home server under option A): a read-only `status.py` and a `reconnect.py`.
- `reconnect.py` is a dry run by default (**unverified** here: the tooling lives outside this repository, so this describes the intended behaviour). `--confirm` performs the real reconnect. It enforces a 15 minute cooldown and a cap of 3 reconnects per day.
- Credentials live in a mode `0600` env file filled in by the owner on the host that runs the tooling. They are never stored in this repository, in `ha/secrets.yaml`, or in Compose.

## Decisions

### 1. Versioning: keep the tooling out of this repository

The tooling goes in its own **private repository**, not in this stack.

- This repository is public configuration-as-code for Home Assistant, Zigbee2MQTT, and Mosquitto. The tooling is a Python project with a vendored third-party client pinned to a commit, a separate virtualenv, and a different lifecycle.
- It handles distributor account access. A separate repository keeps that surface away from the Home Assistant checkout, its CI, and its AI-agent workflows.
- This repository holds only the Home Assistant side of the contract (trigger and notification) and this document.

### 2. Trigger: react to a loss of mains, then confirm with one distributor call

Never poll the distributor. The account may be banned for frequent meter queries, so the distributor is contacted only after a local event, and at most once per attempt.

An attempt starts only when **both** conditions hold:

1. **Local signal (event-driven).** The mains-loss signal stays active for a debounce period (proposed: 2 minutes) so that brief flickers do not start an attempt. Candidate signals are a UPS "on battery" state or a Zigbee mains-powered device going unavailable. **Unverified:** no such entity is defined in tracked configuration. Pick one on the live system and record it before writing the automation.
2. **Distributor confirmation.** One `status.py` call shows the ICP as open (tripped). If the status is anything else (grid outage, supply cut, unknown, or an error), do not reconnect and notify the owner.

`reconnect.py --confirm` runs only after both conditions. Its own cooldown and daily cap are the final gate, and Home Assistant must not bypass them or retry in a loop.

### 3. Host: an always-on host that survives the trip

A trip removes power from everything behind the ICP, including the server, router, and ONT, so the host and its internet path must keep running. Two options:

| Option | How it works | Trade-off |
|---|---|---|
| **A. UPS-backed on-site host (preferred)** | A small host (or the existing server) plus the router/ONT on a UPS. Home Assistant detects mains loss and runs the tooling. | Needs UPS capacity for the router and ONT as well as the host. Fully local trigger. |
| B. Off-site runner | Home Assistant sends a periodic heartbeat to an off-site service. When the heartbeat stops, the runner performs the single status check from decision 2 and re-arms if the ICP is open. | Works if the whole house is down, but a missing heartbeat can also mean an internet or server failure, so the distributor confirmation is mandatory. The heartbeat endpoint and its secret must be protected. |

Option A is the default. Choose B only if a UPS cannot cover the router/ONT. **Unverified:** the UPS model, its runtime, and whether the router/ONT can be powered from it. The owner records the final choice and the measured runtime outside this repository.

If Home Assistant triggers the tooling, do it through a narrow interface (for example a single-purpose HTTP endpoint or command on the tooling host) with its token in `!secret`. Do not mount the tooling, its virtualenv, or its credentials into the Home Assistant container, and do not give Home Assistant the distributor credentials.

## Safety Rules

- Re-arm only after a real trip, as defined by the two conditions above.
- Respect the 15 minute cooldown and the 3 per day cap on every path, including manual runs.
- A trip caused by an overload or an installation fault may not be reconnectable, and repeated re-arming into a fault can be dangerous. On a failed or refused reconnect, stop, notify the owner, and wait for manual action.
- Notify the owner of every attempt and its outcome, including skipped attempts. Do not retry silently.
- The unofficial API can change without notice. Treat an unexpected response as a failure, never as success.
- Do not log credentials, session tokens, or the full response bodies.

## First-run Checklist

These steps need the real account and are pending the owner:

- [ ] `status.py` logs in and lists the supply point and ICP status.
- [ ] A manual `reconnect.py --confirm` re-arms a tripped ICP, and the reconnect action still matches the current distributor web.
- [ ] The host option (A or B) and the mains-loss signal are chosen and recorded.
- [ ] The Home Assistant automation is added with verified entities. Test it with the dry run first. The [README](../README.md#validation) validation covers only the YAML and Compose checks; the drill below covers the automation itself.
- [ ] A drill confirms the automation does not fire on a short flicker and respects the cooldown and daily cap.
