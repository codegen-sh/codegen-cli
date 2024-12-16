from dataclasses import dataclass
from pathlib import Path

from codegen.api.webapp_routes import generate_webapp_url
from codegen.utils.schema import CodemodConfig


@dataclass
class Codemod:
    """Represents a codemod in the local filesystem."""

    name: str
    path: Path
    config: CodemodConfig | None = None

    @property
    def is_active(self) -> bool:
        """Check if this is the currently active codemod."""
        active_file = self.path.parent.parent / "active_codemod.txt"
        if not active_file.exists():
            return False
        return active_file.read_text().strip() == self.name

    def get_url(self) -> str:
        """Get the URL for this codemod."""
        return generate_webapp_url(path=f"codemod/{self.config.codemod_id}")

    def relative_path(self) -> str:
        """Get the relative path to this codemod."""
        return self.path.relative_to(Path.cwd())

    def get_current_source(self) -> str:
        """Get the current source code for this codemod."""
        text = self.path.read_text()
        text = text.strip()
        return text
