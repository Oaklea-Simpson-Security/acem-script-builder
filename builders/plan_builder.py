"""Create project build plans from GitLab snapshots."""

from __future__ import annotations

import logging

from clients.gitlab_client import GitLabClient
from discovery.target_discovery import discover_targets
from models.config_models import BranchSnapshot, BuildPlan, BuildTarget, ProjectConfig, SourceFile
from state.state_store import BuildStateStore


LOGGER = logging.getLogger(__name__)


def build_project_plan(
    client: GitLabClient,
    project: ProjectConfig,
    state_store: BuildStateStore,
) -> BuildPlan | None:
    """Return a build plan when at least one tracked branch changed."""

    branch_snapshots: dict[str, BranchSnapshot] = {}
    changed = False

    for branch in project.branches:
        branch_info = client.get_branch(project.project_id, branch)
        tree_entries = client.list_repository_tree(project.project_id, branch, recursive=True)
        files = {
            entry["path"]: entry["id"]
            for entry in tree_entries
            if entry.get("type") == "blob"
        }
        branch_snapshots[branch] = BranchSnapshot(
            branch=branch,
            commit_sha=branch_info.commit_sha,
            files=files,
        )
        previous_sha = state_store.get_branch_sha(project.project_name, branch)
        if previous_sha != branch_info.commit_sha:
            changed = True

    if not changed:
        LOGGER.info("Skipping %s because tracked branches are unchanged.", project.project_name)
        return None

    main_snapshot = branch_snapshots[project.branches[0]]
    dev_snapshot = branch_snapshots.get(project.branches[1]) if len(project.branches) > 1 else None

    if project.target_mode == "resource_mirror":
        targets = _build_resource_targets(client, project, main_snapshot)
        return BuildPlan(project=project, branch_snapshots=branch_snapshots, targets=targets)

    if dev_snapshot is None:
        raise ValueError(
            f"Project {project.project_name} requires two branches for target_mode={project.target_mode}."
        )

    main_targets = discover_targets(project, main_snapshot)
    dev_targets = discover_targets(project, dev_snapshot)
    all_target_names = sorted(set(main_targets) | set(dev_targets))

    build_targets: list[BuildTarget] = []
    for target_name in all_target_names:
        prod_files = _load_target_files(
            client=client,
            project=project,
            target_name=target_name,
            branch_snapshot=main_snapshot,
            file_paths=main_targets.get(target_name, []),
        )
        dev_files = _load_target_files(
            client=client,
            project=project,
            target_name=target_name,
            branch_snapshot=dev_snapshot,
            file_paths=dev_targets.get(target_name, []),
        )
        output_stem = f"{project.filename_prefix}{target_name}" if project.filename_prefix else target_name
        build_targets.append(
            BuildTarget(
                project_name=project.project_name,
                target_name=target_name,
                output_filename=f"{output_stem}.py",
                prod_files=prod_files,
                dev_files=dev_files,
                stage_order=project.stage_order,
                artifact_kind="combined_script",
            )
        )

    return BuildPlan(project=project, branch_snapshots=branch_snapshots, targets=build_targets)


def _load_target_files(
    client: GitLabClient,
    project: ProjectConfig,
    target_name: str,
    branch_snapshot: BranchSnapshot,
    file_paths: list[str],
) -> list[SourceFile]:
    files: list[SourceFile] = []
    for file_path in sorted(file_paths):
        content = client.get_file_content(project.project_id, branch_snapshot.branch, file_path)
        files.append(
            SourceFile(
                project_name=project.project_name,
                target_name=target_name,
                branch=branch_snapshot.branch,
                file_path=file_path,
                commit_sha=branch_snapshot.commit_sha,
                content=content,
            )
        )
    return files


def _build_resource_targets(
    client: GitLabClient,
    project: ProjectConfig,
    main_snapshot: BranchSnapshot,
) -> list[BuildTarget]:
    target_files = discover_targets(project, main_snapshot)
    build_targets: list[BuildTarget] = []
    for file_path in sorted(target_files):
        prod_files = _load_target_files(
            client=client,
            project=project,
            target_name=file_path,
            branch_snapshot=main_snapshot,
            file_paths=target_files[file_path],
        )
        build_targets.append(
            BuildTarget(
                project_name=project.project_name,
                target_name=file_path,
                output_filename=file_path,
                prod_files=prod_files,
                dev_files=[],
                stage_order=[],
                artifact_kind="raw_file",
            )
        )
    return build_targets
