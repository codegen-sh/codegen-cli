import platform
from typing import Any

from posthog import Posthog

from codegen.cli.analytics.utils import print_debug_message
from codegen.cli.auth.session import CodegenSession
from codegen.cli.env.global_env import global_env


class PostHogTracker:
    session: CodegenSession
    posthog: Posthog

    def __init__(self, session: CodegenSession):
        self.session = session
        self.posthog = Posthog(global_env.POSTHOG_PROJECT_API_KEY, host="https://us.i.posthog.com")

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
            self.posthog.capture(
                distinct_id=self.session.identity.user.github_username,
                event=event_name,
                properties=base_properties,
                groups={"codegen_app": "cli"},
            )
        except Exception as e:
            print_debug_message("Failed to send event to PostHog.")
            print_debug_message(e)
