# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- **`.shellcheckrc`**: strict shellcheck config (forge-patterns standard) — `shell=bash`, `enable=all`, disables SC1091/SC2034
- **`.husky/pre-commit`**: forge-patterns gate — security validation → ruff lint → lint-staged → type check → pytest
- **`.husky/commit-msg`**: conventional commit enforcement (Angular format)
- **`shell-lint` CI job**: shellcheck + shfmt formatting check on all `.sh` files
- **`@uiforge/forge-patterns`**: added as dev dependency (local file reference) for shared constants access

### Changed

- **`engines.node`**: bumped `>=18.0.0` → `>=22.0.0`
- **`NODE_VERSION`** in CI: `"22"` → `"24"` (ci.yml + base-ci.yml default)
- **`node-version`** caller override: `'22'` → `'24'`
- **`ruff>=0.4.0`**: bumped from `>=0.1.0` in dev dependencies
- **`mypy>=1.0.0`**: added to dev dependencies with strict config section in `pyproject.toml`

### Fixed

- **18 shell scripts**: `set -e` → `set -euo pipefail` across all scripts in `scripts/`

## [1.26.0] - 2026-02-18

### 🔧 Pattern Application Phase: UIForge Patterns Integration

- **✅ Prettier Configuration Updated** - Aligned with shared forge-patterns base config
  - Added `$schema` reference to `patterns/code-quality/prettier/base.config.json`
  - Updated `trailingComma` to `es5` (from `none`) per shared standard
  - Updated `arrowParens` to `always` (from `avoid`) per shared standard
  - Preserved project-specific overrides for JSON, YAML, and Markdown files

- **✅ Pattern Validation Script Created** - `scripts/validation/validate-patterns.sh`
  - Validates ESLint and Prettier configs reference shared patterns
  - Checks shared pattern files exist locally
  - Verifies CI/CD uses shared workflows
  - Validates GitHub Actions versions
  - Checks security scanning configuration
  - Non-recursive grep approach to prevent hanging

- **✅ Pre-commit Hooks Updated** - Added `validate-patterns` hook to `.pre-commit-config.yaml`
  - Runs pattern compliance check on every commit
  - Ensures configuration drift is caught early

## [1.25.0] - 2026-02-18

### 🎯 Major Achievement: YAML Migration Validation Complete

- **✅ Migration Validation Script Created** - Comprehensive validation script for configuration files
- **🔍 Configuration Issues Resolved** - All reported YAML validation errors investigated and resolved
