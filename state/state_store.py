"""JSON-backed build state store."""

from __future__ import annotations

import json
from pathlib import Path


class BuildStateStore:
    """Persist and query last processed branch SHAs."""

    def __init__(self, state_path: Path) -> None:
        self.state_path = state_path
        self._state = self._load()

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.state_path.exists():
            return {}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def get_branch_sha(self, project_name: str, branch: str) -> str | None:
        """Return the stored SHA for a project/branch pair."""

        return self._state.get(project_name, {}).get(branch)

    def set_branch_sha(self, project_name: str, branch: str, sha: str) -> None:
        """Update the stored SHA for a project/branch pair."""

        self._state.setdefault(project_name, {})[branch] = sha

    def save(self) -> None:
        """Flush the JSON state file to disk."""

        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(self._state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
