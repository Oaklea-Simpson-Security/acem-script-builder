# Configuration Guide

This guide explains exactly how to configure `acem-script-builder` for your real GitLab projects.

The goal is to help you do this at work even if you do not have every repo detail available right now.

## What You Are Configuring

The builder reads a JSON file at:

- `config/projects.json`

Each object in that JSON array describes one GitLab project the builder should monitor.

You are telling the builder:

- which GitLab project to inspect
- which branch or branches to track
- how to turn repository files into build targets
- which files to include
- which files to ignore
- where to write the generated output locally

## High-Level Rule

You have two different kinds of repositories:

1. Repositories that produce combined Python deployment scripts
2. Repositories that contain raw resources that should be fetched and persisted as files

Use these target modes:

- `leaf_directories`
  Use when each runnable model lives in its own lowest-level folder.

- `whole_project`
  Use when the entire repository should become one target.

- `explicit`
  Use when only certain files belong in a target.

- `resource_mirror`
  Use when files should be downloaded and persisted as-is, not combined into a generated script.

## Your Likely Mapping

Based on your description, your repos probably map like this:

- Fusion-style model repo:
  `leaf_directories`

- Models repo with `Feeds` and `Query Tools`:
  `leaf_directories`

- `acem-utilities`:
  probably `whole_project` now, possibly `explicit` later

- `acem-can-opener`:
  probably `whole_project`

- `JEMA_resources`:
  `resource_mirror`

## Step 1: Find the GitLab Project ID

Each project config needs a `project_id`.

There are two common ways to find it in GitLab:

### Option A: Use the GitLab web UI

1. Open the project in GitLab.
2. Look for a project information panel or settings page.
3. Find the numeric project ID.
4. Copy that number into your config.

### Option B: Use the project URL path if needed later

If you cannot easily find the numeric ID right away, make a temporary note of:

- group name
- subgroup name if any
- project name

Example:

- `acem-team/models`
- `acem-team/shared/acem-utilities`

That helps you come back and fill in the true numeric ID later.

Important:

- In this builder, `project_id` should ultimately be the real GitLab project ID or a GitLab-compatible project identifier accepted by the API.
- Numeric IDs are the safest choice.

## Step 2: Decide the Correct `target_mode`

This is the most important configuration choice.

### Use `leaf_directories` when:

- parent directories are just containers
- each leaf folder is one runnable model
- files inside each leaf folder belong to that one model

This matches structures like:

```text
color-force-fusion/
  color-fusion-worker/
  color-source-one/
  color-source-number_n/
```

and:

```text
Models/
  Feeds/
    acem-feed-one/
    acem-feed-two/
  Query Tools/
    acem-query-tool-one/
    acem-query-tool-n/
```

### Use `whole_project` when:

- the whole repo is one deployable thing
- you do not want separate outputs by directory

This probably fits:

- `acem-utilities`
- `acem-can-opener`

### Use `explicit` when:

- only some files should be included
- folder structure does not match the deployable target
- you want exact control

This is the best long-term mode when directory inference starts breaking down.

### Use `resource_mirror` when:

- the repo should not become a combined script
- files should just be downloaded and persisted
- only one branch matters, such as `main`

This fits:

- `JEMA_resources`

## Step 3: Choose the Branch List

For combined Python outputs, use:

```json
"branches": ["main", "dev"]
```

Why:

- `main` becomes prod-wrapped code
- `dev` becomes dev-wrapped code
- the generated output runs prod first, then dev

For resources, use:

```json
"branches": ["main"]
```

Why:

- you said you only need the main version of resource files
- these files do not need prod/dev script wrapping

## Step 4: Set `root_paths`

`root_paths` tells the builder where to look inside the repository.

### For `leaf_directories`

Use the container directories that hold the real model folders.

Example for a fusion/models-style repo:

```json
"root_paths": [
  "Models/Feeds/",
  "Models/Query Tools/",
  "color-force-fusion/"
]
```

What this means:

- the builder searches under those locations
- it finds Python files
- it groups them by their leaf directory

### For `whole_project`

Usually use:

```json
"root_paths": ["."]
```

What this means:

- search the whole repository

### For `resource_mirror`

Usually use:

```json
"root_paths": ["."]
```

Unless you only want one subfolder. Then use that subfolder path instead.

Example:

```json
"root_paths": ["resources/"]
```

## Step 5: Set the Output Directory

Use `output_root_directory` to choose where files are written locally.

Example:

```json
"output_root_directory": "output"
```

or:

```json
"output_root_directory": "output_resources"
```

How output works now:

- combined script projects write into:
  `output/<project_name>/`

- resource mirror projects write into:
  `output_resources/<project_name>/`

Examples:

- `output/models/acem-feed-one.py`
- `output/acem-utilities/acem-utilities.py`
- `output_resources/JEMA_resources/file_one.json`

## Step 6: Decide Which Files to Include

This is where you reduce noise and avoid pulling unwanted files.

### For Combined Python Script Projects

Usually include only Python:

```json
"include_globs": [
  "*.py",
  "**/*.py"
]
```

### For Resource Repositories

Include the file types you want persisted:

```json
"include_globs": [
  "*.json",
  "*.py",
  "**/*.json",
  "**/*.py"
]
```

If you only want JSON:

```json
"include_globs": [
  "*.json",
  "**/*.json"
]
```

## Step 7: Exclude Files You Do Not Want

Use `exclude_globs` to avoid tests, caches, or irrelevant files.

Common exclusions:

```json
"exclude_globs": [
  "**/__pycache__/**",
  "**/tests/**",
  "**/test/**",
  "**/*.pyc"
]
```

You may also want to exclude:

- notebooks
- docs
- local config files
- archived scripts

For example:

```json
"exclude_globs": [
  "**/__pycache__/**",
  "**/tests/**",
  "**/docs/**",
  "**/*.pyc",
  "**/*.ipynb"
]
```

## Step 8: Decide Whether You Need `whole_project` or `explicit`

This is the most common place where people accidentally choose the wrong mode.

### Use `whole_project` if:

- every relevant Python file in the repo belongs to one output
- you are okay with all included files being part of that target

Example:

```json
{
  "project_name": "acem-utilities",
  "project_id": "456",
  "target_mode": "whole_project",
  "root_paths": ["."],
  "branches": ["main", "dev"],
  "output_root_directory": "output",
  "include_globs": ["*.py", "**/*.py"],
  "exclude_globs": ["**/tests/**", "**/__pycache__/**"]
}
```

### Use `explicit` if:

- only certain files belong in the output
- the repo contains extra scripts, experiments, helpers, or unrelated modules

Example:

```json
{
  "project_name": "acem-utilities",
  "project_id": "456",
  "target_mode": "explicit",
  "branches": ["main", "dev"],
  "output_root_directory": "output",
  "targets": [
    {
      "name": "acem-utilities-core",
      "include_files": [
        "acem_utilities/data_fetcher.py",
        "acem_utilities/preprocessing.py",
        "acem_utilities/processing.py",
        "acem_utilities/output_formatter.py"
      ],
      "exclude_files": []
    }
  ]
}
```

Rule of thumb:

- If you are unsure, start with `whole_project`.
- If the output becomes noisy or wrong, move to `explicit`.

## Step 9: Fill Out the Real Config

Open:

- `config/projects.json`

Replace placeholder values like:

- `"123"`
- `"456"`
- `"789"`
- `"999"`

with the real GitLab project IDs.

Then update the project names if needed so they match the real repos clearly.

Example final shape:

```json
[
  {
    "project_name": "models",
    "project_id": "12345",
    "target_mode": "leaf_directories",
    "root_paths": [
      "Models/Feeds/",
      "Models/Query Tools/"
    ],
    "branches": ["main", "dev"],
    "output_root_directory": "output",
    "include_globs": ["*.py", "**/*.py"],
    "exclude_globs": ["**/__pycache__/**", "**/tests/**"]
  },
  {
    "project_name": "color-force-fusion",
    "project_id": "23456",
    "target_mode": "leaf_directories",
    "root_paths": [
      "color-force-fusion/"
    ],
    "branches": ["main", "dev"],
    "output_root_directory": "output",
    "include_globs": ["*.py", "**/*.py"],
    "exclude_globs": ["**/__pycache__/**", "**/tests/**"]
  },
  {
    "project_name": "acem-utilities",
    "project_id": "34567",
    "target_mode": "whole_project",
    "root_paths": ["."],
    "branches": ["main", "dev"],
    "output_root_directory": "output",
    "include_globs": ["*.py", "**/*.py"],
    "exclude_globs": ["**/__pycache__/**", "**/tests/**"]
  },
  {
    "project_name": "acem-can-opener",
    "project_id": "45678",
    "target_mode": "whole_project",
    "root_paths": ["."],
    "branches": ["main", "dev"],
    "output_root_directory": "output",
    "include_globs": ["*.py", "**/*.py"],
    "exclude_globs": ["**/__pycache__/**", "**/tests/**"]
  },
  {
    "project_name": "JEMA_resources",
    "project_id": "56789",
    "target_mode": "resource_mirror",
    "root_paths": ["."],
    "branches": ["main"],
    "output_root_directory": "output_resources",
    "include_globs": ["*.json", "*.py", "**/*.json", "**/*.py"],
    "exclude_globs": ["**/__pycache__/**", "**/tests/**"]
  }
]
```

## Step 10: Set Your GitLab Token

The script uses the GitLab REST API, so you need a token.

At runtime, set:

- `GITLAB_TOKEN`

Optionally set:

- `GITLAB_BASE_URL`

If your company uses self-hosted GitLab, this may be something like:

```bash
export GITLAB_BASE_URL="https://gitlab.your-company.com"
```

If you use gitlab.com, you can leave it as default.

Set the token:

```bash
export GITLAB_TOKEN="your-token-here"
```

Make sure the token can:

- read project metadata
- read repository trees
- read repository files

## Step 11: Run the Builder

From the repo root:

```bash
python3 main.py --config config/projects.json --state state/build_state.json
```

What happens:

1. The builder loads your config.
2. It checks the latest SHA for each tracked branch.
3. It compares those SHAs with `state/build_state.json`.
4. If nothing changed, it skips that project.
5. If something changed, it rebuilds outputs from current branch HEAD.
6. It writes the outputs locally.
7. It stores the new processed SHAs.

## Step 12: Inspect the Outputs

For script-building projects, check:

- `output/<project_name>/`

For resource mirror projects, check:

- `output_resources/<project_name>/`

Examples:

- `output/models/acem-feed-one.py`
- `output/color-force-fusion/color-source-one.py`
- `output_resources/JEMA_resources/file_one.json`

## How to Think About Common Mistakes

### Mistake 1: Using `whole_project` when the repo contains multiple runnable models

Symptom:

- one giant output file appears when you expected many target files

Fix:

- switch to `leaf_directories`

### Mistake 2: Using `leaf_directories` when the target spans multiple folders

Symptom:

- files you expected are missing from a target
- one logical model gets split incorrectly

Fix:

- use `explicit`

### Mistake 3: Forgetting to exclude tests or junk files

Symptom:

- generated outputs include files you did not expect

Fix:

- tighten `exclude_globs`

### Mistake 4: Putting resource repos into the combined-script pipeline

Symptom:

- JSON/resources get treated like runnable scripts

Fix:

- use `resource_mirror`

### Mistake 5: Assuming directory structure always reflects runtime ownership

Symptom:

- output looks structurally correct but is semantically wrong

Fix:

- move that project to `explicit`

## Recommended Practical Workflow at Work

When you are at work, do this in order:

1. Make a list of the real GitLab repos you want monitored.
2. For each repo, write down:
   - project name
   - numeric GitLab project ID
   - whether it is script-building or resource mirroring
   - whether its targets are leaf directories, whole project, or explicit files
3. Add one project at a time to `config/projects.json`.
4. Run the builder.
5. Inspect the output directory.
6. If the output shape looks wrong, change only the `target_mode` and file filters first.
7. Only move to `explicit` when directory inference is not enough.

## My Strong Recommendation

Start with this:

- `models`: `leaf_directories`
- `color-force-fusion`: `leaf_directories`
- `acem-utilities`: `whole_project`
- `acem-can-opener`: `whole_project`
- `JEMA_resources`: `resource_mirror`

Then promote individual repos to `explicit` only when you see a concrete reason.

That will get you moving without overdesigning too early.

## Files to Look At While Configuring

- `config/projects.json`
- `docs/architecture.md`
- `README.md`

## Suggested Future Improvement

Once you know the real repos well, create a separate config file for work, for example:

- `config/projects.work.json`

That lets you keep:

- sample/demo config in `config/projects.json`
- real internal config in `config/projects.work.json`

Then run:

```bash
python3 main.py --config config/projects.work.json --state state/build_state.json
```

That is usually cleaner and safer.
