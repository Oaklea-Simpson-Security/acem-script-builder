# Work Checklist

Use this as a practical fill-in-the-blanks checklist when you are at work.

## Before You Start

- Confirm you can access the target GitLab instance.
- Confirm you have a GitLab token with repository read access.
- Confirm whether your GitLab is:
  - `https://gitlab.com`
  - or a company-hosted GitLab URL

Write these down:

- GitLab base URL: `____________________________`
- GitLab token available: `yes / no`

## Repos to Configure

For each repository, fill in:

- Project name
- GitLab project ID
- Target mode
- Branches
- Root paths
- Include globs
- Exclude globs
- Output directory

## Repo Worksheet

### 1. Models Repo

- Project name: `____________________________`
- Project ID: `____________________________`
- Target mode: `leaf_directories`
- Branches: `main, dev`
- Root paths:
  - `Models/Feeds/`
  - `Models/Query Tools/`
- Include globs:
  - `*.py`
  - `**/*.py`
- Exclude globs:
  - `**/__pycache__/**`
  - `**/tests/**`
- Output directory:
  - `output`

Questions to confirm:

- Are all runnable models stored in leaf directories?
- Are there any shared parent-level `.py` files that actually belong in the targets?
- Are there any extra folders under `Models/` that should be excluded?

### 2. Fusion Repo

- Project name: `____________________________`
- Project ID: `____________________________`
- Target mode: `leaf_directories`
- Branches: `main, dev`
- Root paths:
  - `color-force-fusion/`
- Include globs:
  - `*.py`
  - `**/*.py`
- Exclude globs:
  - `**/__pycache__/**`
  - `**/tests/**`
- Output directory:
  - `output`

Questions to confirm:

- Are `color-fusion-worker`, `color-source-one`, and similar folders truly separate runnable targets?
- Are there any support files in the parent folder that need to be included?

### 3. acem-utilities

- Project name: `____________________________`
- Project ID: `____________________________`
- Start with target mode: `whole_project`
- Branches: `main, dev`
- Root paths:
  - `.`
- Include globs:
  - `*.py`
  - `**/*.py`
- Exclude globs:
  - `**/__pycache__/**`
  - `**/tests/**`
- Output directory:
  - `output`

Questions to confirm:

- Does the entire repo really belong in one deployable output?
- Are there experiments, scripts, or tools that should not be included?
- If yes, switch to `explicit`.

### 4. acem-can-opener

- Project name: `____________________________`
- Project ID: `____________________________`
- Start with target mode: `whole_project`
- Branches: `main, dev`
- Root paths:
  - `.`
- Include globs:
  - `*.py`
  - `**/*.py`
- Exclude globs:
  - `**/__pycache__/**`
  - `**/tests/**`
- Output directory:
  - `output`

Questions to confirm:

- Is the whole repo one target?
- If not, move to `explicit`.

### 5. JEMA_resources

- Project name: `____________________________`
- Project ID: `____________________________`
- Target mode: `resource_mirror`
- Branches: `main`
- Root paths:
  - `.`
- Include globs:
  - `*.json`
  - `*.py`
  - `**/*.json`
  - `**/*.py`
- Exclude globs:
  - `**/__pycache__/**`
  - `**/tests/**`
- Output directory:
  - `output_resources`

Questions to confirm:

- Do you want both `.json` and `.py`, or only `.json`?
- Are there subfolders that should be excluded?
- Do you want the original directory structure preserved locally? The current builder does preserve it.

## Config Editing Checklist

Open:

- `config/projects.json`

For each project:

1. Replace placeholder `project_name`.
2. Replace placeholder `project_id`.
3. Confirm the `target_mode`.
4. Confirm the `branches`.
5. Confirm the `root_paths`.
6. Tighten `include_globs` if needed.
7. Tighten `exclude_globs` if needed.
8. Save the file.

## Environment Setup Checklist

Set your token:

```bash
export GITLAB_TOKEN="your-token"
```

If needed, set your GitLab base URL:

```bash
export GITLAB_BASE_URL="https://gitlab.your-company.com"
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## First Run Checklist

Run:

```bash
python3 main.py --config config/projects.json --state state/build_state.json
```

Then check:

- Did it connect to GitLab successfully?
- Did it create `output/...` files for script repos?
- Did it create `output_resources/...` files for resource repos?
- Did it update `state/build_state.json`?

## If Something Looks Wrong

If one repo creates one huge output but should create many:

- switch from `whole_project` to `leaf_directories`

If files are missing from a target:

- check `root_paths`
- check `include_globs`
- check `exclude_globs`
- consider switching to `explicit`

If resources are being treated like generated scripts:

- make sure that repo uses `resource_mirror`

If too many files are being mirrored:

- narrow `include_globs`
- add more `exclude_globs`

## Recommended Minimal First Pass

If you are short on time at work, configure only these first:

1. `models`
2. `color-force-fusion`
3. `acem-utilities`
4. `acem-can-opener`
5. `JEMA_resources`

Then run the builder once and inspect the output shape before refining anything else.
