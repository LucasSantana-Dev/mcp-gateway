# Figlet ASCII Art Banners

The MCP CLI tool now features enhanced visual appeal with ASCII art banners using `figlet`.

## Overview

Figlet integration provides stylized command banners that make the CLI more visually appealing and easier to navigate. The implementation includes automatic fallback to simple text banners if figlet is not installed.

## Installation

### macOS

```bash
brew install figlet
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get install figlet
```

### Linux (RHEL/CentOS)

```bash
sudo yum install figlet
```

## Banner Examples

### With Figlet Installed

When figlet is available, commands display stylized ASCII art:

```text
    __  ___________     ______      __
   /  |/  / ____/ __ \ / ____/___ _/ /____  _      ______ _  __
  / /|_/ / /   / /_/ // / __/ __ `/ __/ _ \| | /| / / __ `/ / / /
 / /  / / /___/ ____// /_/ / /_/ / /_/  __/| |/ |/ / /_/ / /_/ /
/_/  /_/\____/_/    \____/\__,_/\__/\___/ |__/|__/\__,_/\__, /
                                                        /____/
Unified CLI Tool

Usage: mcp <command> [options]
```

### Without Figlet (Fallback)

If figlet is not installed, the CLI automatically falls back to simple text banners:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MCP Gateway
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unified CLI Tool

Usage: mcp <command> [options]
```

## Commands with Banners

The following commands feature figlet banners:

### 1. Help / Usage

```bash
./scripts/mcp help
```

Displays "MCP Gateway" banner in blue.

### 2. Start

```bash
./scripts/mcp start
```

Displays "Starting" banner in green.

### 3. IDE Setup

```bash
./scripts/mcp ide setup
```

Displays "IDE Setup" banner in green.

### 4. Doctor (Health Check)

```bash
./scripts/mcp doctor
```

Displays "Health Check" banner in yellow.

## Technical Implementation

### Banner Function

Location: `scripts/mcp`

```bash
# Display banner with figlet (fallback to simple text)
banner() {
    local text="$1"
    local color="${2:-$BLUE}"

    if command -v figlet &> /dev/null; then
        echo -e "${color}"
        figlet -f slant "$text"
        echo -e "${NC}"
    else
        # Fallback to simple banner
        echo ""
        echo -e "${color}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${color}  $text${NC}"
        echo -e "${color}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
    fi
}
```

### Features

1. **Automatic Detection**: Checks if figlet is installed using `command -v figlet`
2. **Graceful Fallback**: Uses simple text banners if figlet unavailable
3. **Color Support**: Accepts color parameter for themed banners
4. **Slant Font**: Uses the "slant" font style for consistent appearance

### Color Scheme

- **Blue** (`$BLUE`): Help/usage, general information
- **Green** (`$GREEN`): Start, setup, success operations
- **Yellow** (`$YELLOW`): Doctor, warnings, diagnostics

## Usage in Scripts

To add a banner to a new command:

```bash
cmd_my_command() {
    banner "My Command" "$GREEN"
    info "Running my command..."
    # ... rest of command logic
}
```

## Benefits

1. **Visual Hierarchy**: Clear command separation and identification
2. **Professional Appearance**: Modern CLI aesthetic
3. **User Experience**: Easier to scan and navigate command output
4. **Accessibility**: Fallback ensures functionality without dependencies
5. **Branding**: Consistent visual identity across CLI commands

## Customization

### Change Font

To use a different figlet font, modify the `banner()` function:

```bash
figlet -f standard "$text"  # Standard font
figlet -f banner "$text"    # Banner font
figlet -f big "$text"       # Big font
```

### List Available Fonts

```bash
figlet -l  # List all installed fonts
```

### Add More Banners

To add banners to additional commands, simply call the `banner()` function at the start of the command:

```bash
cmd_status() {
    banner "Status Check" "$BLUE"
    info "Checking gateway status..."
    # ... command logic
}
```

## See Also

- [MCP CLI Documentation](MCP_CLI.md)
- [Interactive Menu Guide](INTERACTIVE_MENU.md)
- [Figlet Official Documentation](http://www.figlet.org/)
