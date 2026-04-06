"""JSON-backed build state store."""

from __future__ import annotations

import json
import subprocess


class BuildStateStore:
    """Persist and query last processed branch SHAs."""

    def __init__(self, state_path: str) -> None:
        self.state_path = state_path
        self._state = self._load()

    def _load(self) -> dict[str, dict[str, str]]:
        try:
            with open(self.state_path, encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            return {}

    def get_branch_sha(self, project_name: str, branch: str) -> str | None:
        """Return the stored SHA for a project/branch pair."""

        return self._state.get(project_name, {}).get(branch)

    def set_branch_sha(self, project_name: str, branch: str, sha: str) -> None:
        """Update the stored SHA for a project/branch pair."""

        self._state.setdefault(project_name, {})[branch] = sha

    def save(self) -> None:
        """Flush the JSON state file to disk."""

        parent = _parent_directory(self.state_path)
        if parent:
            subprocess.run(["mkdir", "-p", parent], check=True)
        with open(self.state_path, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(self._state, indent=2, sort_keys=True) + "\n")


def _parent_directory(path: str) -> str:
    normalized = path.replace("\\", "/").rstrip("/")
    if "/" not in normalized:
        return ""
    return normalized.rsplit("/", 1)[0]
