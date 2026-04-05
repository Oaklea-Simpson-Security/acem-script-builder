"""Entry point for the ACEM script builder MVP."""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from builders.plan_builder import build_project_plan
from builders.script_generator import generate_combined_script
from clients.gitlab_client import GitLabClient
from models.config_models import load_project_configs
from state.state_store import BuildStateStore
from writers.output_writer import write_build_outputs


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Build combined deployable scripts from GitLab branches.")
    parser.add_argument("--config", default="config/projects.json", help="Path to project config JSON.")
    parser.add_argument("--state", default="state/build_state.json", help="Path to build state JSON.")
    parser.add_argument(
        "--gitlab-base-url",
        default=os.environ.get("GITLAB_BASE_URL", "https://gitlab.com"),
        help="GitLab base URL.",
    )
    parser.add_argument(
        "--gitlab-token",
        default=os.environ.get("GITLAB_TOKEN"),
        help="GitLab private token. Can also be provided via GITLAB_TOKEN.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python logging level.",
    )
    return parser.parse_args()


def configure_logging(level: str) -> None:
    """Configure application logging."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main() -> int:
    """Run the script builder."""

    args = parse_args()
    configure_logging(args.log_level)
    logger = logging.getLogger(__name__)

    if not args.gitlab_token:
        raise SystemExit("A GitLab token is required. Set GITLAB_TOKEN or pass --gitlab-token.")

    config_path = Path(args.config)
    state_path = Path(args.state)
    projects = load_project_configs(config_path)
    state_store = BuildStateStore(state_path)
    client = GitLabClient(args.gitlab_base_url, args.gitlab_token)

    for project in projects:
        logger.info("Evaluating project %s", project.project_name)
        plan = build_project_plan(client, project, state_store)
        if plan is None:
            continue

        rendered: dict[str, str] = {}
        for target in plan.targets:
            if target.artifact_kind == "combined_script":
                rendered[target.target_name] = generate_combined_script(target)
            elif target.artifact_kind == "raw_file":
                rendered[target.target_name] = target.prod_files[0].content if target.prod_files else ""
            else:
                raise ValueError(f"Unsupported artifact kind: {target.artifact_kind}")
        written_paths = write_build_outputs(plan, rendered)
        for branch, snapshot in plan.branch_snapshots.items():
            state_store.set_branch_sha(project.project_name, branch, snapshot.commit_sha)
        logger.info(
            "Built %s target(s) for %s: %s",
            len(written_paths),
            project.project_name,
            ", ".join(str(path) for path in written_paths),
        )

    state_store.save()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
