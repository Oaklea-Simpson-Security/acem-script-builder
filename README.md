# ACEM Script Builder

`acem-script-builder` builds deployable single-file Python scripts from GitLab branch contents.

It is designed for processing environments with these constraints:

- only one Python file can be deployed
- GitLab cannot connect directly to the processing environment
- only the latest generated artifact can be persisted
- the processing environment starts from scratch on each run

The builder solves that by:

- reading repository contents from the GitLab REST API
- discovering build targets per project
- fetching Python files from `main` and `dev`
- generating one combined artifact per target
- embedding ordered stage sources from both branches into the artifact
- exposing runtime helpers such as `run_both("processing")`
- executing `prod` first and `dev` second for the selected stage
- mirroring raw resource files for repos that should not go through the combined-script pipeline

## Project Layout

- `main.py`: entry point
- `config/`: JSON configuration
- `state/`: SHA tracking state
- `clients/`: GitLab API client
- `discovery/`: target discovery strategies
- `builders/`: build planning and artifact generation
- `writers/`: filesystem output writers
- `models/`: shared dataclasses and config/state models
- `examples/`: example generated artifact
- `output/`: default local output directory

## Run

Set `GITLAB_TOKEN` and optionally `GITLAB_BASE_URL`, then run:

```bash
python3 main.py --config config/projects.json --state state/build_state.json
```

## Opinionated v1 Notes

- Directory discovery is useful for fast onboarding, but it is not a reliable long-term ownership model.
- The sustainable source of truth is an explicit target manifest, even when leaf-directory discovery is used initially.
- v1 rebuilds an entire target from both branch heads whenever either tracked branch changes.
- v1 preserves source file contents as embedded stage source strings instead of aggressively rewriting imports.
- v1 expects the generated script to be called through dispatch helpers such as `run_both("<stage_name>")`.
- v1 also supports `resource_mirror` for non-script assets such as JSON resources that should be fetched from `main` and persisted as raw files.
