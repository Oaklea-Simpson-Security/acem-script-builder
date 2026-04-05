"""Resolve build targets from repository trees."""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import PurePosixPath

from models.config_models import BranchSnapshot, ExplicitTargetConfig, ProjectConfig


def _is_python_file(path: str, extensions: list[str]) -> bool:
    return PurePosixPath(path).suffix in extensions


def _matches_any(path: str, globs: list[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in globs)


def _is_included(path: str, project: ProjectConfig) -> bool:
    if not _is_python_file(path, project.python_extensions):
        return False
    if project.include_globs and not _matches_any(path, project.include_globs):
        return False
    if project.exclude_globs and _matches_any(path, project.exclude_globs):
        return False
    return True


def _leaf_directory_targets(project: ProjectConfig, snapshot: BranchSnapshot) -> dict[str, list[str]]:
    directory_to_files: dict[str, list[str]] = {}
    for path in snapshot.files:
        if not _is_included(path, project):
            continue
        for root in project.root_paths:
            normalized_root = root.strip("/")
            normalized_path = path.strip("/")
            if normalized_root and not normalized_path.startswith(normalized_root):
                continue
            parent = str(PurePosixPath(path).parent)
            directory_to_files.setdefault(parent, []).append(path)

    all_directories = set(directory_to_files.keys())
    leaf_targets: dict[str, list[str]] = {}
    for directory, files in sorted(directory_to_files.items()):
        is_parent = any(
            other != directory and other.startswith(f"{directory}/")
            for other in all_directories
        )
        if not is_parent:
            leaf_targets[PurePosixPath(directory).name] = sorted(files)
    return leaf_targets


def _whole_project_targets(project: ProjectConfig, snapshot: BranchSnapshot) -> dict[str, list[str]]:
    included: list[str] = []
    normalized_roots = [root.strip("/") for root in project.root_paths if root]
    for path in snapshot.files:
        if not _is_included(path, project):
            continue
        if normalized_roots:
            normalized_path = path.strip("/")
            if not any(
                root == "." or not root or normalized_path.startswith(root)
                for root in normalized_roots
            ):
                continue
        included.append(path)
    included.sort()
    return {project.project_name: included}


def _explicit_targets(project: ProjectConfig, snapshot: BranchSnapshot) -> dict[str, list[str]]:
    available = set(snapshot.files.keys())
    targets: dict[str, list[str]] = {}
    for target in project.targets:
        targets[target.name] = _resolve_explicit_target(target, available)
    return targets


def _resource_mirror_targets(project: ProjectConfig, snapshot: BranchSnapshot) -> dict[str, list[str]]:
    included: dict[str, list[str]] = {}
    normalized_roots = [root.strip("/") for root in project.root_paths if root and root != "."]
    for path in sorted(snapshot.files):
        if project.include_globs and not _matches_any(path, project.include_globs):
            continue
        if project.exclude_globs and _matches_any(path, project.exclude_globs):
            continue
        if normalized_roots:
            normalized_path = path.strip("/")
            if not any(normalized_path.startswith(root) for root in normalized_roots):
                continue
        included[path] = [path]
    return included


def _resolve_explicit_target(target: ExplicitTargetConfig, available_files: set[str]) -> list[str]:
    include_set = {path for path in target.include_files if path in available_files}
    exclude_set = set(target.exclude_files)
    return sorted(include_set - exclude_set)


def discover_targets(project: ProjectConfig, snapshot: BranchSnapshot) -> dict[str, list[str]]:
    """Discover target names and included files from a single branch snapshot."""

    if project.target_mode == "leaf_directories":
        return _leaf_directory_targets(project, snapshot)
    if project.target_mode == "whole_project":
        return _whole_project_targets(project, snapshot)
    if project.target_mode == "explicit":
        return _explicit_targets(project, snapshot)
    if project.target_mode == "resource_mirror":
        return _resource_mirror_targets(project, snapshot)
    raise ValueError(f"Unsupported target_mode: {project.target_mode}")
