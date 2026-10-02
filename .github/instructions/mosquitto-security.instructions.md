---
name: Mosquitto Broker Security Guidance
description: Source-backed security guidance for the tracked Mosquitto broker configuration.
applyTo: "mosquitto/config/mosquitto.conf"
---

# Mosquitto Broker Configuration

- Preserve `allow_anonymous false` and the configured password-file path unless an explicitly approved change requires otherwise.
- Treat listener, authentication, and transport-security changes as security-sensitive; request a Home Security Reviewer review before implementation.
- Never read, copy, or expose password-file contents, and never place credentials in this configuration.
- Verify related claims against tracked Compose and Mosquitto configuration only; do not infer live broker state.
- Do not start or restart the broker as part of validation.