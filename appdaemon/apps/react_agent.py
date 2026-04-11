"""ReAct (Reason + Act) Agentic AI for Home Assistant.

Implements three autonomous agents that use an LLM with tool-calling to
perform multi-step reasoning and home control actions:

  - MorningBriefingAgent : runs at 08:00 on weekdays
  - WelcomeHomeAgent     : runs when person.destaben arrives home
  - SecuritySweepAgent   : runs every night at 23:30

Safety guardrails (enforced at code level):
  - Forbidden services (alarm disable, door unlock) are always blocked
  - Max MAX_AGENT_CALLS service calls per agent run (rate limit)
  - input_boolean.agent_dry_run: when ON, agent plans but does not execute
  - All actions logged with [AI_AGENT] tag

References: destaben/homeassistant#16
"""

import base64
import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import appdaemon.plugins.hass.hassapi as hass
import requests

# Maximum number of LLM tool calls allowed per agent run.
MAX_AGENT_CALLS = 10

# HA entity that enables dry-run mode (agent plans but does not act).
DRY_RUN_ENTITY = "input_boolean.agent_dry_run"

# Primary notification target.
NOTIFY_SERVICE = "notify/mobile_app_davids_iphone"

# Directory where camera snapshots are stored (mapped to /config inside container).
SNAPSHOT_DIR = "/config/www/snapshots"

# Heater smart plug entity ID (referenced in multiple agent prompts).
HEATER_ENTITY_ID = "switch.smart_plug_1909121534757325186448e1e903790b_outlet"

# Services the agent is NEVER permitted to call, regardless of LLM reasoning.
FORBIDDEN_SERVICES: set[tuple[str, str]] = {
    ("alarm_control_panel", "alarm_disarm"),
    ("alarm_control_panel", "alarm_trigger"),
    ("lock", "unlock"),
}

# ---------------------------------------------------------------------------
# Tool schema (OpenAI function-calling format)
# ---------------------------------------------------------------------------

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_entity_state",
            "description": (
                "Get the current state and attributes of a Home Assistant entity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The Home Assistant entity ID (e.g. 'light.light_1').",
                    }
                },
                "required": ["entity_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_service",
            "description": (
                "Call a Home Assistant service to control a device. "
                "NEVER call services that disable the alarm or unlock doors."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Service domain, e.g. 'light', 'switch', 'vacuum'.",
                    },
                    "service": {
                        "type": "string",
                        "description": "Service name, e.g. 'turn_on', 'turn_off', 'start'.",
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Target entity ID.",
                    },
                    "data": {
                        "type": "object",
                        "description": "Optional service data (e.g. brightness, temperature).",
                    },
                },
                "required": ["domain", "service", "entity_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_history",
            "description": "Get state history for an entity for the last N hours.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The Home Assistant entity ID.",
                    },
                    "hours": {
                        "type": "integer",
                        "description": "Number of past hours of history to retrieve (max 48).",
                    },
                },
                "required": ["entity_id", "hours"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_camera",
            "description": (
                "Take a snapshot from a camera and analyze it with vision AI. "
                "Returns a textual description answering the question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "camera_entity_id": {
                        "type": "string",
                        "description": "Camera entity ID, e.g. 'camera.tapo_camera_2f13_hd_stream'.",
                    },
                    "question": {
                        "type": "string",
                        "description": "Question to answer about the camera image.",
                    },
                },
                "required": ["camera_entity_id", "question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_notification",
            "description": "Send a push notification to the owner's phone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Notification title."},
                    "message": {"type": "string", "description": "Notification body."},
                },
                "required": ["title", "message"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_BASE = (
    "You are an autonomous home automation AI agent. "
    "You have access to tools to read and control a Home Assistant smart home. "
    "Think step by step, use tools to gather information, then act. "
    "Always log your reasoning. "
    "SAFETY RULES (never violate): "
    "1. Never disable the alarm or unlock doors autonomously. "
    "2. Never call alarm_control_panel.alarm_disarm or lock.unlock. "
    "3. Limit total tool calls to {max_calls}. "
    "4. When done, call send_notification with a concise summary for the owner."
).format(max_calls=MAX_AGENT_CALLS)

MORNING_SYSTEM = _SYSTEM_BASE
MORNING_TASK = (
    "Run the morning briefing for the home owner. "
    "1. Check if person.destaben is home. "
    "2. Check the current temperature from any available temperature sensor. "
    f"3. Check the state of the heater ({HEATER_ENTITY_ID}). "
    "4. Check the air purifier state (fan.zhimi_mc2_8977_air_purifier). "
    "5. Compose a friendly morning briefing message and send it as a notification. "
    "Include: presence, temperature, heater status, and any recommendations."
)

WELCOME_SYSTEM = _SYSTEM_BASE
WELCOME_TASK = (
    "The home owner has just arrived home. Prepare a comfortable welcome. "
    "1. Check the current time to determine which lights to turn on. "
    "2. Check the temperature (any available sensor). "
    "3. Turn on appropriate lights based on the time of day: "
    "   - Daytime (07:00-19:00): turn on light.light_1. "
    "   - Evening/night (19:00-07:00): turn on light.light_1 and light.light_2. "
    "4. If temperature is below 19°C, turn on the heater "
    f"   (call_service domain=switch service=turn_on entity_id={HEATER_ENTITY_ID}). "
    "5. Send a welcome home notification summarizing what was done."
)

SECURITY_SYSTEM = _SYSTEM_BASE
SECURITY_TASK = (
    "Run the nightly security sweep. "
    "1. Check the front door sensor (binary_sensor.door_1_contact). "
    "2. Check all window sensors: binary_sensor.window_1_contact, "
    "   binary_sensor.window_2_contact, binary_sensor.window_3_contact. "
    "3. Check that all lights are off (switch.light, light.yeelink_color3_6f42_light). "
    "4. Check the alarm automation state (automation.alarm). "
    "5. Take a camera snapshot and analyze it: "
    "   analyze_camera(camera_entity_id='camera.tapo_camera_2f13_hd_stream', "
    "   question='Is there anything unusual or suspicious visible?'). "
    "6. Send a security summary notification. "
    "If anything is open or looks suspicious, mark the notification as urgent."
)


# ---------------------------------------------------------------------------
# Base ReAct Agent
# ---------------------------------------------------------------------------


class ReActAgent(hass.Hass):
    """Base class implementing the ReAct (Reason + Act) loop.

    Subclasses must call ``super().initialize()`` and define their own
    ``initialize()`` to schedule or listen for triggers.
    """

    def initialize(self) -> None:
        self.api_url: str = self.args.get("api_url", "https://api.openai.com/v1")
        self.api_key: str = self.args.get("api_key", "")
        self.model: str = self.args.get("model", "gpt-4o-mini")
        self.agent_name: str = self.args.get("agent_name", self.__class__.__name__)
        self._lock = threading.Lock()
        self.log(f"[AI_AGENT] {self.agent_name} initialized (model={self.model})")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run_agent(self, system_prompt: str, task: str) -> Optional[str]:
        """Execute the ReAct loop for *task* and return the final response."""
        if not self._lock.acquire(blocking=False):
            self.log(
                f"[AI_AGENT] {self.agent_name} is already running — skipping.",
                level="WARNING",
            )
            return None

        try:
            return self._react_loop(system_prompt, task)
        finally:
            self._lock.release()

    # ------------------------------------------------------------------
    # ReAct loop
    # ------------------------------------------------------------------

    def _react_loop(self, system_prompt: str, task: str) -> Optional[str]:
        dry_run = self._is_dry_run()
        mode_label = "DRY-RUN" if dry_run else "LIVE"
        self.log(
            f"[AI_AGENT] {self.agent_name} starting [{mode_label}]: {task[:100]}",
            level="INFO",
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]

        call_count = 0

        while True:
            response = self._call_llm(messages)
            if response is None:
                self.log(
                    f"[AI_AGENT] {self.agent_name} LLM call failed — aborting.",
                    level="ERROR",
                )
                return None

            choice = response["choices"][0]
            assistant_msg = choice["message"]
            messages.append(assistant_msg)

            finish_reason = choice.get("finish_reason", "stop")

            if finish_reason == "stop":
                result = assistant_msg.get("content", "")
                self.log(
                    f"[AI_AGENT] {self.agent_name} completed after {call_count} tool calls.",
                    level="INFO",
                )
                return result

            if finish_reason == "tool_calls":
                tool_calls = assistant_msg.get("tool_calls", [])
                for tc in tool_calls:
                    if call_count >= MAX_AGENT_CALLS:
                        self.log(
                            f"[AI_AGENT] {self.agent_name} hit rate limit "
                            f"({MAX_AGENT_CALLS} calls) — stopping.",
                            level="WARNING",
                        )
                        self.call_service(
                            NOTIFY_SERVICE,
                            title=f"[AI_AGENT] {self.agent_name} rate-limited",
                            message=(
                                f"Agent stopped after {MAX_AGENT_CALLS} tool calls "
                                "to prevent runaway loops."
                            ),
                        )
                        return None

                    call_count += 1
                    tool_result = self._dispatch_tool(tc, dry_run)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": json.dumps(tool_result),
                        }
                    )

            else:
                self.log(
                    f"[AI_AGENT] {self.agent_name} unexpected finish_reason={finish_reason!r}",
                    level="WARNING",
                )
                return assistant_msg.get("content")

    # ------------------------------------------------------------------
    # LLM API call
    # ------------------------------------------------------------------

    def _call_llm(self, messages: list) -> Optional[dict]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "tools": AGENT_TOOLS,
                "tool_choice": "auto",
            }
            url = f"{self.api_url.rstrip('/')}/chat/completions"
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            self.log(f"[AI_AGENT] LLM request error: {exc}", level="ERROR")
            return None
        except Exception as exc:
            self.log(f"[AI_AGENT] Unexpected LLM error: {exc}", level="ERROR")
            return None

    # ------------------------------------------------------------------
    # Tool dispatcher
    # ------------------------------------------------------------------

    def _dispatch_tool(self, tool_call: dict, dry_run: bool) -> Any:
        name = tool_call["function"]["name"]
        try:
            args: dict = json.loads(tool_call["function"].get("arguments", "{}"))
        except json.JSONDecodeError:
            args = {}

        self.log(f"[AI_AGENT] Tool call: {name}({args})", level="INFO")

        if name == "get_entity_state":
            return self._get_entity_state(**args)
        if name == "call_service":
            return self._call_ha_service(dry_run=dry_run, **args)
        if name == "get_history":
            return self._get_history(**args)
        if name == "analyze_camera":
            return self._analyze_camera(dry_run=dry_run, **args)
        if name == "send_notification":
            return self._send_notification(dry_run=dry_run, **args)

        return {"error": f"Unknown tool: {name!r}"}

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    def _get_entity_state(self, entity_id: str) -> dict:
        try:
            state = self.get_state(entity_id, attribute="all")
            if state is None:
                return {"error": f"Entity not found: {entity_id!r}"}
            return {
                "entity_id": entity_id,
                "state": state.get("state"),
                "attributes": state.get("attributes", {}),
                "last_changed": state.get("last_changed", ""),
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _call_ha_service(
        self,
        domain: str,
        service: str,
        entity_id: str,
        data: Optional[dict] = None,
        dry_run: bool = False,
    ) -> dict:
        # Safety: block forbidden service combinations
        if (domain, service) in FORBIDDEN_SERVICES:
            msg = f"BLOCKED (safety guardrail): {domain}.{service} is not permitted."
            self.log(f"[AI_AGENT] {msg}", level="WARNING")
            return {"error": msg}

        # Extra guard: never autonomously turn off the alarm automation
        if domain == "automation" and service == "turn_off" and "alarm" in entity_id:
            msg = "BLOCKED (safety guardrail): Cannot disable the alarm automation."
            self.log(f"[AI_AGENT] {msg}", level="WARNING")
            return {"error": msg}

        self.log(
            f"[AI_AGENT] call_service {domain}.{service} → {entity_id} data={data}",
            level="INFO",
        )

        if dry_run:
            return {
                "dry_run": True,
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "data": data,
            }

        try:
            service_data: dict = {"entity_id": entity_id}
            if data:
                service_data.update(data)
            self.call_service(f"{domain}/{service}", **service_data)
            return {
                "success": True,
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _get_history(self, entity_id: str, hours: int) -> dict:
        try:
            hours = min(int(hours), 48)
            days_float = hours / 24.0
            history = self.get_history(entity_id=entity_id, days=days_float)
            if not history:
                return {"entity_id": entity_id, "hours": hours, "history": []}

            # Flatten and simplify for LLM consumption (cap at 20 entries)
            raw = history[0] if history and isinstance(history[0], list) else history
            simplified = [
                {
                    "state": entry.get("state"),
                    "last_changed": entry.get("last_changed", ""),
                }
                for entry in raw
            ]
            return {
                "entity_id": entity_id,
                "hours": hours,
                "history": simplified[-20:],
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _analyze_camera(
        self,
        camera_entity_id: str,
        question: str,
        dry_run: bool = False,
    ) -> dict:
        if dry_run:
            return {
                "dry_run": True,
                "camera": camera_entity_id,
                "question": question,
                "result": "(dry-run — no snapshot taken)",
            }

        # 1. Take snapshot
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_filename = f"agent_cam_{ts}.jpg"
        snapshot_path = f"{SNAPSHOT_DIR}/{snapshot_filename}"

        try:
            os.makedirs(SNAPSHOT_DIR, exist_ok=True)
            self.call_service(
                "camera/snapshot",
                entity_id=camera_entity_id,
                filename=snapshot_path,
            )
            # Give HA a moment to write the file
            time.sleep(3)
        except Exception as exc:
            return {"error": f"Snapshot failed: {exc}"}

        # 2. Attempt vision analysis via LLM if image exists
        if not os.path.isfile(snapshot_path):
            return {
                "camera": camera_entity_id,
                "question": question,
                "snapshot_path": snapshot_path,
                "note": "Snapshot not found on disk — vision analysis skipped.",
            }

        try:
            with open(snapshot_path, "rb") as fh:
                b64_image = base64.b64encode(fh.read()).decode("utf-8")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            vision_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}"
                            },
                        },
                    ],
                }
            ]
            payload = {"model": self.model, "messages": vision_messages, "max_tokens": 300}
            url = f"{self.api_url.rstrip('/')}/chat/completions"
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            result_text = resp.json()["choices"][0]["message"]["content"]
            return {
                "camera": camera_entity_id,
                "question": question,
                "analysis": result_text,
                "snapshot_path": snapshot_path,
            }
        except Exception as exc:
            return {
                "camera": camera_entity_id,
                "question": question,
                "snapshot_path": snapshot_path,
                "note": f"Vision analysis failed: {exc}",
            }

    def _send_notification(
        self,
        title: str,
        message: str,
        dry_run: bool = False,
    ) -> dict:
        self.log(
            f"[AI_AGENT] Notification — {title}: {message[:120]}",
            level="INFO",
        )
        if dry_run:
            return {"dry_run": True, "title": title, "message": message}
        try:
            self.call_service(NOTIFY_SERVICE, title=title, message=message)
            return {"success": True, "title": title}
        except Exception as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_dry_run(self) -> bool:
        try:
            return self.get_state(DRY_RUN_ENTITY) == "on"
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Concrete Agent: Morning Briefing (08:00 on weekdays)
# ---------------------------------------------------------------------------


class MorningBriefingAgent(ReActAgent):
    """Sends a personalised morning briefing every weekday at 08:00."""

    def initialize(self) -> None:
        super().initialize()
        self.run_daily(
            self._on_trigger,
            "08:00:00",
            constrain_days="mon,tue,wed,thu,fri",
        )
        self.log("[AI_AGENT] MorningBriefingAgent scheduled at 08:00 weekdays.")

    def _on_trigger(self, kwargs: dict) -> None:
        self.run_in(lambda _: self.run_agent(MORNING_SYSTEM, MORNING_TASK), 0)


# ---------------------------------------------------------------------------
# Concrete Agent: Welcome Home (person.destaben arrives)
# ---------------------------------------------------------------------------


class WelcomeHomeAgent(ReActAgent):
    """Prepares the home whenever person.destaben arrives."""

    def initialize(self) -> None:
        super().initialize()
        self.listen_state(self._on_arrive, "person.destaben", new="home")
        self.log("[AI_AGENT] WelcomeHomeAgent listening for person.destaben → home.")

    def _on_arrive(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict
    ) -> None:
        self.run_in(lambda _: self.run_agent(WELCOME_SYSTEM, WELCOME_TASK), 0)


# ---------------------------------------------------------------------------
# Concrete Agent: Nightly Security Sweep (23:30 every day)
# ---------------------------------------------------------------------------


class SecuritySweepAgent(ReActAgent):
    """Performs a full security sweep every night at 23:30."""

    def initialize(self) -> None:
        super().initialize()
        self.run_daily(self._on_trigger, "23:30:00")
        self.log("[AI_AGENT] SecuritySweepAgent scheduled at 23:30 daily.")

    def _on_trigger(self, kwargs: dict) -> None:
        self.run_in(lambda _: self.run_agent(SECURITY_SYSTEM, SECURITY_TASK), 0)
