from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar

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


class CodemodManager:
    """Manages codemod operations in the local filesystem."""

    CODEMODS_DIR: ClassVar[Path] = Path.cwd() / ".codegen" / "codemods"

    @classmethod
    def list(cls) -> list[Codemod]:
        """List all codemods in the codemods directory."""
        if not cls.CODEMODS_DIR.exists():
            return []

        codemods = []
        for codemod_dir in cls.CODEMODS_DIR.iterdir():
            if not codemod_dir.is_dir():
                continue

            run_file = codemod_dir / "run.py"
            config_file = codemod_dir / "config.json"

            if not run_file.exists():
                continue

            # Try to load config if it exists
            config = None
            if config_file.exists():
                try:
                    config = CodemodConfig.model_validate_json(config_file.read_text())
                except Exception:
                    pass  # Config is optional

            codemods.append(
                Codemod(
                    name=codemod_dir.name,
                    path=run_file,
                    config=config,
                )
            )

        return codemods

    @classmethod
    def create(
        cls,
        name: str,
        code: str,
        codemod_id: int | None = None,
        description: str | None = None,
        author: str | None = None,
    ) -> Codemod:
        """Create a new codemod.

        Args:
            name: Name of the codemod (will be converted to snake_case)
            code: Source code for the codemod
            codemod_id: Optional ID from the server
            description: Optional description
            author: Optional author name

        Returns:
            Codemod: The created codemod

        Raises:
            ValueError: If a codemod with this name already exists
        """
        # Ensure valid codemod name
        codemod_name = name.lower().replace(" ", "_").replace("-", "_")

        # Setup paths
        cls.CODEMODS_DIR.mkdir(parents=True, exist_ok=True)
        codemod_dir = cls.CODEMODS_DIR / codemod_name
        run_file = codemod_dir / "run.py"
        config_file = codemod_dir / "config.json"

        if codemod_dir.exists():
            raise ValueError(f"Codemod '{codemod_name}' already exists at {codemod_dir}")

        # Create directory and files
        codemod_dir.mkdir()
        run_file.write_text(code)

        # Create config if we have an ID
        config = None
        if codemod_id is not None:
            config = CodemodConfig(
                name=codemod_name,
                codemod_id=codemod_id,
                description=description or f"Codemod: {name}",
                created_at=datetime.now().isoformat(),
                created_by=author or "Unknown",
            )
            config_file.write_text(config.model_dump_json(indent=2))

        # Set as active codemod
        with (cls.CODEMODS_DIR / "active_codemod.txt").open("w") as f:
            f.write(codemod_name)

        return Codemod(name=codemod_name, path=run_file, config=config)
