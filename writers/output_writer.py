"""Write generated artifacts to disk."""

from __future__ import annotations

from pathlib import Path

from models.config_models import BuildPlan


def write_build_outputs(plan: BuildPlan, rendered_targets: dict[str, str]) -> list[Path]:
    """Write all rendered outputs for a build plan."""

    output_dir = Path(plan.project.output_root_directory) / plan.project.project_name
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for target in plan.targets:
        payload = rendered_targets[target.target_name]
        output_path = output_dir / target.output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
        written.append(output_path)
    return written
