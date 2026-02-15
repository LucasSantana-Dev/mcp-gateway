# Phase 4 & 5 Implementation Plan

**Date:** 2026-02-15
**Strategy:** Parallel Development
**Status:** Planning

---

## 🎯 Overview

Executing **Phase 4 (Admin UI Enhancement)** and **Phase 5 (Command Simplification)** in parallel to maximize development velocity.

### Phase 4: Admin UI Enhancement (Primary Track)
**Goal:** Visual management interface for server lifecycle
**Priority:** High
**Estimated Duration:** 3-5 days

### Phase 5: Command Simplification (Secondary Track)
**Goal:** Streamline common operations with unified CLI
**Priority:** Medium
**Estimated Duration:** 2-3 days (can overlap)

---

## 📋 Phase 4: Admin UI Enhancement

### Architecture Analysis

**Current State:**
- ✅ REST API endpoints ready (`/api/virtual-servers`)
- ✅ Backend lifecycle management complete
- ⏳ Context Forge Admin UI exists but needs extension
- ⏳ No custom UI components yet

**Context Forge Integration:**
- Admin UI accessible at `http://localhost:4444/admin`
- Built with IBM Context Forge (existing system)
- Need to extend with custom pages/components
- `uiforge` service in docker-compose.yml (port 8026)

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Admin UI (Context Forge)                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Server Management Dashboard                  │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  ServerList Component                         │  │   │
│  │  │  - Fetch servers from REST API                │  │   │
│  │  │  - Display in table/grid format               │  │   │
│  │  │  - Real-time status indicators                │  │   │
│  │  │  - Enable/disable toggles                     │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  ServerCard Component                         │  │   │
│  │  │  - Individual server details                  │  │   │
│  │  │  - Status badge (enabled/disabled)            │  │   │
│  │  │  - Toggle switch                              │  │   │
│  │  │  - Gateway list                               │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  IDEConfigGenerator Component                 │  │   │
│  │  │  - Form for IDE selection                     │  │   │
│  │  │  - Server selection dropdown                  │  │   │
│  │  │  - Generate button                            │  │   │
│  │  │  - Copy-to-clipboard button                   │  │   │
│  │  │  - Preview of generated config                │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step 1: Research & Setup (Day 1)
- [x] Analyze Context Forge Admin UI structure
- [ ] Identify extension points for custom pages
- [ ] Set up development environment for UI work
- [ ] Review React best practices for admin dashboards

#### Step 2: Core Components (Days 2-3)
- [ ] **ServerList Component**
  - Fetch servers from `GET /api/virtual-servers`
  - Display in responsive table/grid
  - Add loading and error states
  - Implement pagination if needed

- [ ] **ServerCard Component**
  - Display server name and gateways
  - Status badge (enabled/disabled)
  - Toggle switch for enable/disable
  - Call `PATCH /api/virtual-servers/{name}`
  - Optimistic UI updates

- [ ] **StatusIndicator Component**
  - Real-time status display
  - Color-coded badges (green/gray)
  - Optional: polling for updates
  - Optional: WebSocket integration

#### Step 3: IDE Config Generator (Day 3)
- [ ] **IDEConfigGenerator Component**
  - Form with IDE selection (Windsurf/Cursor)
  - Server selection dropdown
  - Gateway URL input
  - JWT token input (optional)
  - Generate button
  - Display generated JSON
  - Copy-to-clipboard button

#### Step 4: Integration & Polish (Days 4-5)
- [ ] Integrate components into Context Forge Admin UI
- [ ] Add real-time updates (polling every 5s)
- [ ] Implement copy-to-clipboard functionality
- [ ] Add loading states and error handling
- [ ] Mobile-responsive design
- [ ] Accessibility improvements (ARIA labels)
- [ ] End-to-end testing

### Technical Stack

**Frontend:**
- React 18+ (Context Forge base)
- TypeScript (if Context Forge uses it)
- Tailwind CSS or Context Forge styling
- React hooks (useState, useEffect, useCallback)
- Fetch API for REST calls

**Key Features:**
- Real-time updates via polling (5s interval)
- Optimistic UI updates
- Error boundaries
- Loading skeletons
- Toast notifications for success/error

### API Integration

```typescript
// Example API service
const serverAPI = {
  list: () => fetch('/api/virtual-servers').then(r => r.json()),
  get: (name: string) => fetch(`/api/virtual-servers/${name}`).then(r => r.json()),
  update: (name: string, enabled: boolean) =>
    fetch(`/api/virtual-servers/${name}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    }).then(r => r.json())
};
```

### Success Metrics

- [ ] <3 clicks to enable/disable server ✅
- [ ] Real-time UI updates (<500ms latency) ✅
- [ ] Mobile-responsive design ✅
- [ ] Zero errors in production ✅
- [ ] 100% accessibility score ✅

---

## 📋 Phase 5: Command Simplification

### Current State Analysis

**Existing Commands:**
```bash
# Current workflow (complex)
make start                          # Start gateway
make register                       # Register servers
make ide-config IDE=windsurf        # Generate IDE config
# Manual: Copy config to IDE settings
```

**Pain Points:**
- Multiple commands required
- Manual config copying
- No IDE auto-detection
- No interactive guidance
- Scattered documentation

### Unified CLI Architecture

```
mcp
├── init                 # Initialize project (one-time setup)
├── start                # Start gateway with smart defaults
├── stop                 # Stop gateway
├── status               # Check gateway health
├── server
│   ├── list             # List all servers
│   ├── enable <name>    # Enable server
│   ├── disable <name>   # Disable server
│   └── info <name>      # Get server details
├── ide
│   ├── setup            # Interactive IDE setup wizard
│   ├── config           # Generate IDE config
│   └── detect           # Auto-detect installed IDEs
└── wizard               # Interactive setup wizard
```

### Implementation Steps

#### Step 1: CLI Tool Design (Day 1)
- [ ] Design command structure
- [ ] Choose CLI framework (Click/Typer for Python or Commander.js for Node)
- [ ] Define argument parsing
- [ ] Plan interactive prompts

#### Step 2: Core Commands (Day 2)
- [ ] **mcp init** - Initialize project
  - Check prerequisites (Docker, docker-compose)
  - Create .env from template
  - Run initial setup

- [ ] **mcp start** - Start gateway
  - Run `docker compose up -d`
  - Wait for health check
  - Display status

- [ ] **mcp server** - Server management
  - Wrap existing Makefile commands
  - Add interactive selection

#### Step 3: Interactive Wizard (Day 3)
- [ ] **mcp wizard** - Setup wizard
  - Detect installed IDEs
  - Select servers to enable
  - Generate IDE config
  - Copy to clipboard
  - Provide next steps

- [ ] **mcp ide setup** - IDE setup
  - Auto-detect Windsurf/Cursor
  - Select server
  - Generate config
  - Offer to copy to settings

#### Step 4: Polish & Documentation (Day 3)
- [ ] Add help text for all commands
- [ ] Create man pages
- [ ] Update README with new CLI
- [ ] Add shell completions (bash/zsh)

### Technical Implementation

**Option A: Python CLI (Recommended)**
```python
# cli/mcp.py
import click

@click.group()
def cli():
    """MCP Gateway unified CLI tool."""
    pass

@cli.command()
def init():
    """Initialize MCP Gateway project."""
    click.echo("Initializing MCP Gateway...")
    # Implementation

@cli.group()
def server():
    """Manage virtual servers."""
    pass

@server.command()
def list():
    """List all virtual servers."""
    # Call REST API or read config

if __name__ == '__main__':
    cli()
```

**Option B: Bash Script (Simpler)**
```bash
#!/usr/bin/env bash
# scripts/mcp

case "$1" in
    init)
        ./scripts/init.sh
        ;;
    start)
        make start
        ;;
    server)
        case "$2" in
            list) make list-enabled ;;
            enable) make enable-server SERVER="$3" ;;
            disable) make disable-server SERVER="$3" ;;
        esac
        ;;
    wizard)
        ./scripts/wizard.sh
        ;;
esac
```

### IDE Auto-Detection

```python
import os
from pathlib import Path

def detect_ides():
    """Detect installed IDEs."""
    ides = []

    # Windsurf
    windsurf_paths = [
        Path.home() / ".windsurf",
        Path.home() / "Library/Application Support/Windsurf"
    ]
    if any(p.exists() for p in windsurf_paths):
        ides.append("windsurf")

    # Cursor
    cursor_paths = [
        Path.home() / ".cursor",
        Path.home() / "Library/Application Support/Cursor"
    ]
    if any(p.exists() for p in cursor_paths):
        ides.append("cursor")

    return ides
```

### Success Metrics

- [ ] <2 min from install to first connection ✅
- [ ] 80% reduction in command complexity ✅
- [ ] Zero configuration for local development ✅
- [ ] Interactive wizard completion rate >90% ✅

---

## 🔄 Parallel Development Strategy

### Week 1 Schedule

**Days 1-2: Foundation**
- Phase 4: Research Context Forge, design components
- Phase 5: Design CLI architecture, choose framework

**Days 3-4: Core Implementation**
- Phase 4: Build ServerList and ServerCard components
- Phase 5: Implement core CLI commands (init, start, server)

**Day 5: Integration**
- Phase 4: IDE config generator UI
- Phase 5: Interactive wizard

**Days 6-7: Polish & Testing**
- Phase 4: Real-time updates, mobile responsive
- Phase 5: Shell completions, documentation
- Both: End-to-end testing, documentation updates

### Risk Mitigation

**Phase 4 Risks:**
- Context Forge extension complexity → Fallback: standalone React app
- REST API integration issues → Already tested, low risk
- Real-time updates performance → Use polling as fallback

**Phase 5 Risks:**
- CLI framework choice → Start with bash, migrate to Python if needed
- IDE auto-detection accuracy → Manual fallback always available
- Cross-platform compatibility → Test on macOS/Linux/Windows

---

## 📊 Success Criteria

### Phase 4 Complete When:
- [ ] Server list displays all servers with status
- [ ] Enable/disable toggles work correctly
- [ ] IDE config generator produces valid JSON
- [ ] Copy-to-clipboard works on all browsers
- [ ] Real-time updates refresh every 5s
- [ ] Mobile-responsive on all screen sizes
- [ ] All tests passing

### Phase 5 Complete When:
- [ ] `mcp` command available system-wide
- [ ] All subcommands implemented and tested
- [ ] Interactive wizard guides new users
- [ ] IDE auto-detection works on macOS/Linux
- [ ] Documentation complete
- [ ] Shell completions available

---

## 📝 Next Actions

1. **Immediate (Phase 4):**
   - Read Context Forge Admin UI documentation
   - Identify custom page extension points
   - Create React component scaffolding

2. **Immediate (Phase 5):**
   - Choose CLI framework (Python Click vs Bash)
   - Create `scripts/mcp` entry point
   - Implement `mcp init` command

3. **Documentation:**
   - Update PROJECT_CONTEXT.md with progress
   - Create component documentation
   - Write CLI usage guide

---

**Last Updated:** 2026-02-15
**Status:** Planning Complete → Ready for Implementation
