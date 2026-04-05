"""Minimal GitLab REST API client for branch and file discovery."""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from urllib.parse import quote

import requests


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class GitLabProjectBranch:
    """Branch metadata needed by the builder."""

    name: str
    commit_sha: str


class GitLabClient:
    """Thin wrapper around the GitLab REST API."""

    def __init__(
        self,
        base_url: str,
        private_token: str,
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"PRIVATE-TOKEN": private_token})

    def _request(self, method: str, path: str, params: dict[str, str] | None = None) -> dict:
        url = f"{self.base_url}/api/v4{path}"
        response = self.session.request(
            method,
            url,
            params=params,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def list_repository_tree(
        self,
        project_id: str,
        branch: str,
        path: str = "",
        recursive: bool = True,
    ) -> list[dict]:
        """List repository tree entries."""

        params = {
            "ref": branch,
            "recursive": "true" if recursive else "false",
            "per_page": "100",
        }
        if path and path != ".":
            params["path"] = path

        page = 1
        results: list[dict] = []
        while True:
            paged_params = {**params, "page": str(page)}
            chunk = self._request("GET", f"/projects/{quote(project_id, safe='')}/repository/tree", paged_params)
            if not chunk:
                break
            if not isinstance(chunk, list):
                raise ValueError("Unexpected repository tree response from GitLab.")
            results.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
        return results

    def get_branch(self, project_id: str, branch: str) -> GitLabProjectBranch:
        """Fetch branch metadata including its tip SHA."""

        payload = self._request(
            "GET",
            f"/projects/{quote(project_id, safe='')}/repository/branches/{quote(branch, safe='')}",
        )
        return GitLabProjectBranch(
            name=payload["name"],
            commit_sha=payload["commit"]["id"],
        )

    def get_file_content(self, project_id: str, branch: str, file_path: str) -> str:
        """Fetch and decode one repository file."""

        payload = self._request(
            "GET",
            f"/projects/{quote(project_id, safe='')}/repository/files/{quote(file_path, safe='')}",
            {"ref": branch},
        )
        raw = base64.b64decode(payload["content"])
        return raw.decode("utf-8")
