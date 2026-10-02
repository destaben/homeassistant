---
name: Home Assistant Core Configuration
description: Source-backed guidance for Home Assistant configuration, scripts, and scenes in this repository.
applyTo: "ha/{configuration,scripts,scenes}.yaml"
---

# Home Assistant Core Configuration

- Read the complete target file and related included files before editing.
- Verify entities, services, and integration assumptions from tracked configuration; never infer live state.
- Preserve existing syntax and add focused configuration only. Do not reorganize unrelated sections.
- Keep secrets out of tracked YAML and use `!secret` only with a corresponding placeholder key when a new secret is required.
- Validate YAML and require the live Home Assistant configuration check before production reloads or restarts.