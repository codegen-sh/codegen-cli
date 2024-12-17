import json
import os
import platform
import uuid
from typing import Any

import posthog

from codegen.analytics.utils import print_debug_message
from codegen.auth.config import ANALYTICS_FILE
from codegen.auth.session import CodegenSession
from codegen.env.global_env import global_env


class PostHogTracker:
    session: CodegenSession

    def __init__(self, session: CodegenSession):
        self.session = session
        self._initialize_posthog()
        self._initialize_config()

    def _initialize_posthog(self):
        """Initialize PostHog with the given API key and host."""
        # posthog.api_key = api_key
        posthog.project_api_key = global_env.POSTHOG_PROJECT_API_KEY
        posthog.personal_api_key = global_env.POSTHOG_API_KEY
        posthog.host = "https://us.i.posthog.com"

    def _initialize_config(self):
        """Initialize or load the config file."""
        # check if the analytical config file exists
        if not os.path.exists(ANALYTICS_FILE):
            distinct_id = str(uuid.uuid4())
            telemetry_enabled = True
            with open(ANALYTICS_FILE, "w") as f:
                json.dump({"distinct_id": distinct_id, "telemetry_enabled": telemetry_enabled}, f)

        # load the config file
        with open(ANALYTICS_FILE) as f:
            data = json.load(f)
            self.session.config.analytics.distinct_id = data["distinct_id"]
            self.session.config.analytics.telemetry_enabled = data["telemetry_enabled"]

    def opt_in(self, opted_in: bool = True):
        with open(ANALYTICS_FILE, "w") as f:
            data = json.load(f)
            data["telemetry_enabled"] = opted_in
            json.dump(data, f)

    def opt_out(self):
        """Opt out of telemetry."""
        self.opt_in(False)

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

        if not self.session.config.analytics.telemetry_enabled:
            print_debug_message("User not opted_in. Posthog message won't be sent! ")
            return

        try:
            posthog.capture(distinct_id=self.session.config.analytics.distinct_id, event=event_name, properties=base_properties, groups={"codegen_app": "cli"})
        except Exception as e:
            # Silently fail for telemetry
            print_debug_message("Failed to send event to PostHog.")
            print_debug_message(e)
