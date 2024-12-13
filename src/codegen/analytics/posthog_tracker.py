import json
import os
import platform
import time
import uuid
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any

import posthog

from codegen.analytics.constants import POSTHOG_TRACKER


def print_debug_message(message):
    if os.environ.get("DEBUG"):
        print(message)


class PostHogTracker:
    def __init__(self):
        self.config_file = ".config.json"

        self._initialize_posthog()
        self._initialize_config()
        self.opted_in = self.config.get("telemetry_enabled", False)
        self.distinct_id = self.config.get("distinct_id")

    def _initialize_posthog(self):
        """Initialize PostHog with the given API key and host."""
        # posthog.api_key = api_key
        posthog.project_api_key = os.environ.get("POSTHOG_PROJECT_API_KEY")
        posthog.personal_api_key = os.environ.get("POSTHOG_API_KEY")
        posthog.host = "https://us.i.posthog.com"

    def _initialize_config(self):
        """Initialize or load the config file."""
        # check if config_file exists
        if Path(self.config_file).is_file():
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
            posthog.capture(distinct_id=self.distinct_id, event=event_name, properties=base_properties)
        except Exception as e:
            # Silently fail for telemetry
            print("Failed to send event to PostHog")
            print(e)
            pass


@contextmanager
def track_command_execution(command_name: str):
    """Context manager to track command execution time and success."""
    start_time = time.time()
    success = True
    try:
        yield
    except BaseException:
        success = False
        raise
    finally:
        duration = time.time() - start_time
        print_debug_message(f"Command {command_name} took {duration:.2f} seconds")
        POSTHOG_TRACKER.capture_event(f"cli_command_{command_name}", {"duration": duration, "success": success, "command": command_name})
        print_debug_message(f"Command {command_name} execution tracked")


def track_command():
    """Decorator to track command execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with track_command_execution(func.__name__):
                return func(*args, **kwargs)

        return wrapper

    return decorator
