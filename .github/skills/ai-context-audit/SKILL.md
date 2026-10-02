---
name: ai-context-audit
description: "Audit repository documentation and AI context for accuracy, ownership, discoverability, stale claims, and secret safety. Use when reviewing AGENTS.md, Copilot instructions, custom agents, instructions, prompts, skills, README content, or related documentation drift."
argument-hint: "Describe the documentation or AI-context area to audit."
user-invocable: true
---

# AI Context Audit

## When to Use

- Review documentation after configuration, repository-layout, or AI-customization changes.
- Audit `AGENTS.md`, Copilot instructions, agents, instructions, prompts, skills, or README content.
- Check for stale operational claims, duplicated guidance, missing customization discovery, or accidental secret exposure.

## Procedure

1. Inventory the applicable tracked documentation and workspace customization locations:
   - `AGENTS.md`
   - `README.md`
   - `.github/copilot-instructions.md`
   - `.github/agents/`
   - `.github/instructions/`
   - `.github/prompts/`
   - `.github/skills/`
2. Identify the owning document and tracked source for each claim. Use configuration files for configured facts; do not treat ignored runtime files, logs, backups, secrets, or live state as documentation sources.
3. Check that custom agent and skill frontmatter includes a specific, keyword-rich `description`; confirm each skill folder name matches its `name` field; and confirm file instructions have an intentionally narrow `applyTo` pattern.
4. Remove or label unverified claims about live deployment status, entity registries, integrations, GitHub issue state, and recovery outcomes. Preserve only claims that can be supported by tracked files or an explicitly queried external source.
5. Keep shared guidance in `AGENTS.md`, concise Copilot context in `.github/copilot-instructions.md`, and human operational guidance in `README.md`. Prefer references over copying detailed facts between them.
6. Confirm every modified document is English-only, contains no credentials or sensitive values, and does not instruct agents to inspect ignored secret or runtime data.
7. Validate Markdown paths, frontmatter, and the final diff. Report changes, verified sources, validation performed, and deferred findings.

## Boundaries

- Do not change Home Assistant, Docker Compose, Mosquitto, or Zigbee2MQTT configuration during a documentation audit.
- Do not add global `applyTo: "**"` instructions, lifecycle hooks, or broad capabilities merely to enforce documentation review.
- Keep the audit non-blocking: report unrelated drift for follow-up instead of expanding the requested work without approval.