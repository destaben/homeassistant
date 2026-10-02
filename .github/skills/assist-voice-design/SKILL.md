---
name: assist-voice-design
description: "Design safe Home Assistant Assist and conversation capabilities. Use when adding voice commands, custom sentences, conversation automations, intent scripts, or LLM-assisted home control."
argument-hint: "Describe the spoken command, language, expected response, and target behavior."
user-invocable: true
---

# Assist and Voice Design

## Procedure

1. Confirm the required integration and target entities are configured and tracked.
2. Define narrow intents or commands, sample utterances, expected responses, and no-match behavior.
3. Use scripts as constrained action boundaries where a command can affect several entities.
4. Require confirmation for consequential behavior and reject requests involving security disablement or secret disclosure.
5. Test through Assist and the Home Assistant configuration checker after configuration changes.

## Design Principle

Expose the minimum capability needed for the spoken task. Do not use an LLM as an unrestricted control plane for the home.