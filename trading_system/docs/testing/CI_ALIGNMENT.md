# CI Alignment

## Existing CI workflows found
- No `.github/workflows/*.yml` files were found in this repository.

## Issues discovered
- Quality commands were runnable locally but not codified in CI.
- Baseline `mypy .` failed before this pass due to package-layout assumptions.

## Changes made in this pass
- Added `[tool.mypy]` config in `pyproject.toml`:
  - `explicit_package_bases = true`
  - `ignore_missing_imports = true`
- Updated README/testing docs to publish canonical local commands.

## Canonical local commands to mirror in CI
1. `ruff check .`
2. `mypy .`
3. `pytest -q`

## Remaining gaps
- No actual CI pipeline file yet; next pass should add workflow definitions and cache strategy.
- No container-image build validation job (and no Dockerfile present to build).
