"""Write generated artifacts to disk."""

from __future__ import annotations

import subprocess

from models.config_models import BuildPlan


def write_build_outputs(plan: BuildPlan, rendered_targets: dict[str, str]) -> list[str]:
    """Write all rendered outputs for a build plan."""

    output_dir = _join_path(plan.project.output_root_directory, plan.project.project_name)
    subprocess.run(["mkdir", "-p", output_dir], check=True)
    written: list[str] = []
    for target in plan.targets:
        payload = rendered_targets[target.target_name]
        output_path = _join_path(output_dir, target.output_filename)
        parent = _parent_directory(output_path)
        if parent:
            subprocess.run(["mkdir", "-p", parent], check=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(payload)
        written.append(output_path)
    return written


def _join_path(left: str, right: str) -> str:
    if not left:
        return right
    return left.rstrip("/\\") + "/" + right.lstrip("/\\")


def _parent_directory(path: str) -> str:
    normalized = path.replace("\\", "/").rstrip("/")
    if "/" not in normalized:
        return ""
    return normalized.rsplit("/", 1)[0]
