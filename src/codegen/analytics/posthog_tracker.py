import json
import platform
import uuid
from pathlib import Path
from typing import Any

import posthog

from codegen.analytics.utils import print_debug_message
from codegen.auth.config import CODEGEN_DIR
from codegen.env.global_env import global_env


class PostHogTracker:
    def __init__(self):
        self.config_dir = Path.cwd() / CODEGEN_DIR
        self.config_file = self.config_dir / "config.json"

        self._initialize_posthog()
        self._initialize_config()
        self.opted_in = self.config.get("telemetry_enabled", False)
        self.distinct_id = self.config.get("distinct_id")

    def _initialize_posthog(self):
        """Initialize PostHog with the given API key and host."""
        # posthog.api_key = api_key
        posthog.project_api_key = global_env.POSTHOG_PROJECT_API_KEY
        posthog.personal_api_key = global_env.POSTHOG_API_KEY
        posthog.host = "https://us.i.posthog.com"

    def _initialize_config(self):
        """Initialize or load the config file."""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Check if config file exists
        if self.config_file.is_file():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            # Create new config with defaults
            self.config = {"telemetry_enabled": False, "distinct_id": str(uuid.uuid4())}
            self._save_config()

    def _save_config(self):
        """Save the current configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def opt_in(self):
        """Opt in to telemetry."""
        self.opted_in = True
        self.config["telemetry_enabled"] = True
        self._save_config()

    def opt_out(self):
        """Opt out of telemetry."""
        self.opted_in = False
        self.config["telemetry_enabled"] = False
        self._save_config()

    def capture_event(self, event_name: str, properties: dict[str, Any] | None = None):
        """Capture an event if user has opted in."""
        # Add default properties
        base_properties = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
        }

        if properties:
            base_properties.update(properties)

        print_debug_message(f"About to send: {event_name} with properties: {base_properties}")

        if not self.opted_in:
            print_debug_message("User not opted_in. Posthog message won't be sent! ")
            return

        try:
            posthog.capture(distinct_id=self.distinct_id, event=event_name, properties=base_properties, groups={"codegen_app": "cli"})
        except Exception as e:
            # Silently fail for telemetry
            print("Failed to send event to PostHog")
            print(e)
            pass
