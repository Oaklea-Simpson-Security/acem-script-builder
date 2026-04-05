# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project currently uses date-based unreleased notes while the MVP is taking shape.

## [Unreleased]

### Added

- Initial Python MVP for building combined deployable scripts from GitLab branch contents.
- Config-driven project support for `leaf_directories`, `whole_project`, and `explicit` target modes.
- `resource_mirror` target mode for non-script resources that should be fetched and persisted as raw files from a tracked branch.
- GitLab REST API client for branch metadata, repository tree discovery, and repository file retrieval.
- JSON-backed state tracking for last processed branch SHAs.
- Build planning pipeline that rebuilds project outputs when either tracked branch changes.
- Combined script generator that emits:
  - metadata header
  - runtime logging/output helpers
  - prod wrappers generated from `main`
  - dev wrappers generated from `dev`
  - prod-first then dev dispatch execution
  - guarded execution so failures are isolated by wrapper and by stage
- Local output writer for generated artifacts.
- Example project configuration in `config/projects.json`.
- Example generated artifact in `examples/generated_example.py`.
- Architecture notes in `docs/architecture.md`.
- Basic run documentation in `README.md`.
- Dependency declaration in `requirements.txt`.

### Notes

- The MVP preserves file contents inside generated wrappers instead of attempting aggressive import rewriting.
- Directory-based grouping is supported for now, but the recommended long-term direction is a manifest-first, explicit target model.
