# Architecture Migration Guide

## Overview

This document describes the migration from a flat project structure to a monorepo-style architecture completed on **February 15, 2026**.

## Migration Summary

### What Changed

**Before (Flat Structure):**
```
mcp-gateway/
├── tool_router/           # Python backend (mixed with tests)
├── web-admin/             # Next.js app at root
├── src/                   # TypeScript client
├── config/                # Mixed environment configs
├── scripts/               # Unorganized scripts
├── Dockerfile.*           # Multiple Dockerfiles at root
└── docker-compose.yml
```

**After (Monorepo Structure):**
```
mcp-gateway/
├── apps/
│   ├── tool-router/       # Python MCP server
│   │   ├── src/tool_router/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── web-admin/         # Next.js admin UI
│   │   ├── src/
│   │   └── package.json
│   └── mcp-client/        # TypeScript client
│       ├── src/
│       └── package.json
├── config/
│   ├── development/
│   ├── production/
│   └── test/
├── docker/
│   └── docker-compose.yml
└── scripts/
```

### Key Improvements

1. **✅ Removed Legacy Code** (0% coverage duplicates)
   - `tool_router/server.py` → `tool_router/core/server.py`
   - `tool_router/gateway_client.py` → `tool_router/gateway/client.py`
   - `tool_router/scoring.py` → `tool_router/scoring/matcher.py`
   - `tool_router/args.py` → `tool_router/args/builder.py`

2. **✅ Consolidated Tests**
   - Moved `test_*.py` from root to `tests/unit/`
   - Organized: `tests/unit/`, `tests/integration/`, `tests/e2e/`
   - Module tests remain: `ai/tests/`, `api/tests/`, `core/tests/`

3. **✅ Clear App Boundaries**
   - Each app in `apps/` is self-contained
   - Independent `package.json`/`pyproject.toml`
   - Can be built/tested/deployed separately

4. **✅ Environment Separation**
   - `config/development/` - Local dev configs
   - `config/production/` - Production configs
   - `config/test/` - Test configs

## Migration Script

The migration was automated using `scripts/migrate-architecture.sh`:

```bash
# Dry run (preview changes)
./scripts/migrate-architecture.sh --dry-run

# Execute migration
./scripts/migrate-architecture.sh

# Rollback if needed (uses automatic backup)
# Backup location: .migration-backup-YYYYMMDD-HHMMSS/
```

### Migration Phases

1. **Phase 1**: Create directory structure
2. **Phase 2**: Move tool-router to `apps/tool-router/src/`
3. **Phase 3**: Remove legacy duplicate files
4. **Phase 4**: Consolidate test files
5. **Phase 5**: Update import paths
6. **Phase 6**: Move web-admin to `apps/web-admin/`
7. **Phase 7**: Move mcp-client to `apps/mcp-client/`
8. **Phase 8**: Reorganize config by environment
9. **Phase 9**: Move Docker files

## Updated Workflows

### Development

```bash
# Tool Router (Python)
cd apps/tool-router
python -m pytest tests/ -v
python -m pytest tests/ --cov=src/tool_router --cov-report=html

# Web Admin (Next.js)
cd apps/web-admin
npm run dev
npm run build

# MCP Client (TypeScript)
cd apps/mcp-client
npm run build
npm run test
```

### Docker

```bash
# Start all services
cd docker
docker-compose up -d

# Build specific app
docker build -f apps/tool-router/Dockerfile -t mcp-tool-router .
```

### Testing

```bash
# Run all tests from root
make test

# Test specific app
cd apps/tool-router && pytest tests/

# Coverage report
cd apps/tool-router && pytest tests/ --cov=src/tool_router --cov-report=html
```

## Import Path Changes

### Python Imports

**Before:**
```python
from tool_router.server import execute_task
from tool_router.gateway_client import get_tools
from tool_router.scoring import pick_best_tools
from tool_router.args import build_arguments
```

**After:**
```python
from tool_router.core.server import execute_task
from tool_router.gateway.client import get_tools
from tool_router.scoring.matcher import select_top_matching_tools
from tool_router.args.builder import build_arguments
```

### Configuration Paths

**Before:**
```python
config_file = Path("config/features.yaml")
```

**After:**
```python
# From apps/tool-router/
config_file = Path("../../config/development/features.yaml")

# Or use environment variable
config_env = os.getenv("CONFIG_ENV", "development")
config_file = Path(f"../../config/{config_env}/features.yaml")
```

## CI/CD Updates Needed

### GitHub Actions

Update workflow paths:

```yaml
# Before
- name: Test
  run: pytest tool_router/tests/

# After
- name: Test Tool Router
  working-directory: apps/tool-router
  run: pytest tests/

- name: Test Web Admin
  working-directory: apps/web-admin
  run: npm test
```

### Docker Compose

Update service paths:

```yaml
# Before
services:
  tool-router:
    build:
      context: .
      dockerfile: Dockerfile.tool-router

# After
services:
  tool-router:
    build:
      context: .
      dockerfile: apps/tool-router/Dockerfile
```

## Rollback Procedure

If issues arise, rollback using the automatic backup:

```bash
# 1. Find backup directory
ls -la .migration-backup-*

# 2. Restore from backup
BACKUP_DIR=".migration-backup-20260215-220635"

# 3. Restore directories
rm -rf tool_router web-admin src config scripts
cp -r ${BACKUP_DIR}/tool_router .
cp -r ${BACKUP_DIR}/web-admin .
cp -r ${BACKUP_DIR}/src .
cp -r ${BACKUP_DIR}/config .
cp -r ${BACKUP_DIR}/scripts .

# 4. Restore config files
cp ${BACKUP_DIR}/pyproject.toml .
cp ${BACKUP_DIR}/docker-compose.yml .

# 5. Remove apps/ directory
rm -rf apps/

# 6. Run tests to verify
make test
```

## Benefits Achieved

### Code Quality
- ✅ Removed 4 legacy files with 0% test coverage
- ✅ Consolidated 3 scattered test files
- ✅ Clear module boundaries

### Maintainability
- ✅ Each app is self-contained
- ✅ Independent versioning possible
- ✅ Easier to onboard new developers

### Scalability
- ✅ Can add new apps easily
- ✅ Shared packages in `packages/` (future)
- ✅ Independent deployment pipelines

### Testing
- ✅ Consistent test organization
- ✅ Clear test types: unit/integration/e2e
- ✅ Maintained ≥85% coverage

## Next Steps

1. **Update CI/CD** - Modify GitHub Actions workflows
2. **Update Documentation** - README.md, PROJECT_CONTEXT.md
3. **Docker Compose** - Update service paths
4. **Makefile** - Update targets for new structure
5. **IDE Config** - Update `.windsurf/` and `.cursor/` paths

## Lessons Learned

### What Worked Well
- Automated migration script with dry-run
- Automatic backup before changes
- Incremental phases with validation
- Import path updates via sed

### Improvements for Future
- Add more validation checks between phases
- Create migration tests
- Document environment-specific configs better
- Add migration verification script

## References

- Migration Script: `scripts/migrate-architecture.sh`
- Backup Location: `.migration-backup-YYYYMMDD-HHMMSS/`
- Architecture Docs: `docs/architecture/OVERVIEW.md`
- Project Context: `PROJECT_CONTEXT.md`

---

**Migration Date**: February 15, 2026
**Migration Tool**: `scripts/migrate-architecture.sh`
**Status**: ✅ Complete
**Test Coverage**: Maintained ≥85%
