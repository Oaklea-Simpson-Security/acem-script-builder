# Architecture Recommendation

## Opinionated Take

Directory-based grouping is a useful bootstrap mechanism, not a durable build contract.

It works when:

- every runnable target lives in its own leaf directory
- Python files within that directory truly belong to that one runnable unit
- the repo does not share files across targets through sibling imports or non-directory ownership rules

It breaks when:

- a repo contains support files at a parent directory that are logically part of one target
- one target spans multiple directories
- only some files in a directory belong in the deployable output
- directories are organized for humans or teams rather than runtime packaging
- targets require shared libraries that should not be bundled into unrelated outputs

That is why `leaf_directories` is fine for v1 discovery, but explicit target manifests are the sustainable end state.

## Recommended v1

Use a config-driven orchestrator with three target modes:

- `leaf_directories`: fast adoption for repos already shaped like runnable leaf models
- `whole_project`: one repo equals one deployable output
- `explicit`: exact file lists for cases where ownership does not match directories
- `resource_mirror`: raw files copied from a tracked branch without script wrapping

Core v1 pipeline:

1. Load project configs.
2. Query GitLab branch metadata for tracked branches.
3. Compare branch tip SHAs against local state.
4. If either branch changed, fetch current trees for both branches.
5. Discover targets using the configured mode.
6. Fetch target Python files from both branches.
7. Generate one combined output per target.
8. Write local artifacts and update stored SHAs.

For resource repositories:

1. Track only `main` unless there is a real need for environment comparison.
2. Fetch matching files such as `.json` and approved `.py` resource files.
3. Persist them locally with their repository-relative paths intact.
4. Do not wrap or combine them into generated runtime scripts.

Important v1 bias:

- Rebuild full outputs from current branch HEADs.
- Do not attempt incremental patching of generated files.
- Keep generation deterministic and transparent.

## Recommended v2

Move from "discovery-first" to "manifest-first".

Add:

- versioned target manifests committed alongside source code
- per-target execution strategy metadata
- file ordering rules for deterministic runtime sequencing
- optional dependency inlining rules for approved internal libraries
- content hashing by target, not just branch SHA tracking
- generated artifact validation before publish
- structured output adapters instead of plain `print`

Most important v2 shift:

Model the deployable unit directly instead of inferring it from folder shape.

## Biggest Technical Risk

The current MVP executes each source file in an isolated wrapper using `exec`.
That is robust for preserving source text and isolating failures, but it will not
magically solve normal Python module imports between files that used to live in a package.

If a target relies on sibling imports, you will need one of these next:

- shared stage namespace execution
- import rewriting to local generated symbols
- explicit entrypoint-only execution instead of file-by-file execution
- packaging metadata that tells the builder how to inline modules safely

The current MVP is intentionally honest about that limitation instead of pretending bundling is solved.
