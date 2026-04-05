"""Configuration and shared datamodels."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExplicitTargetConfig:
    """Explicit file list for a single output target."""

    name: str
    include_files: list[str]
    exclude_files: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectConfig:
    """Configuration for one GitLab project."""

    project_name: str
    project_id: str
    target_mode: str
    branches: list[str]
    output_root_directory: str
    root_paths: list[str] = field(default_factory=list)
    targets: list[ExplicitTargetConfig] = field(default_factory=list)
    include_globs: list[str] = field(default_factory=lambda: ["*.py", "**/*.py"])
    exclude_globs: list[str] = field(default_factory=list)
    python_extensions: list[str] = field(default_factory=lambda: [".py"])
    filename_prefix: str = ""
    stage_order: list[str] = field(
        default_factory=lambda: [
            "data_fetcher.py",
            "preprocessing.py",
            "processing.py",
            "output_formatter.py",
        ]
    )


@dataclass(slots=True)
class BranchSnapshot:
    """Repository branch tip and tree snapshot."""

    branch: str
    commit_sha: str
    files: dict[str, str]


@dataclass(slots=True)
class SourceFile:
    """A single Python file included in an output target."""

    project_name: str
    target_name: str
    branch: str
    file_path: str
    commit_sha: str
    content: str


@dataclass(slots=True)
class BuildTarget:
    """Resolved target with included files from one or more branches."""

    project_name: str
    target_name: str
    output_filename: str
    prod_files: list[SourceFile]
    dev_files: list[SourceFile]
    stage_order: list[str]
    artifact_kind: str = "combined_script"


@dataclass(slots=True)
class BuildPlan:
    """A project-level build plan."""

    project: ProjectConfig
    branch_snapshots: dict[str, BranchSnapshot]
    targets: list[BuildTarget]


def load_project_configs(config_path: Path) -> list[ProjectConfig]:
    """Load a JSON array of project configs from disk."""

    import json

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    projects: list[ProjectConfig] = []
    for item in raw:
        explicit_targets = [
            ExplicitTargetConfig(
                name=target["name"],
                include_files=target.get("include_files", []),
                exclude_files=target.get("exclude_files", []),
            )
            for target in item.get("targets", [])
        ]
        projects.append(
            ProjectConfig(
                project_name=item["project_name"],
                project_id=str(item["project_id"]),
                target_mode=item["target_mode"],
                branches=item.get("branches", ["main", "dev"]),
                output_root_directory=item.get("output_root_directory", "output"),
                root_paths=item.get("root_paths", []),
                targets=explicit_targets,
                include_globs=item.get("include_globs", ["*.py", "**/*.py"]),
                exclude_globs=item.get("exclude_globs", []),
                python_extensions=item.get("python_extensions", [".py"]),
                filename_prefix=item.get("filename_prefix", ""),
                stage_order=item.get(
                    "stage_order",
                    [
                        "data_fetcher.py",
                        "preprocessing.py",
                        "processing.py",
                        "output_formatter.py",
                    ],
                ),
            )
        )
    return projects


def dump_json(data: dict[str, Any], path: Path) -> None:
    """Write JSON with stable formatting."""

    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
