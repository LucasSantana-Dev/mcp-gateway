# MCP Gateway Quick Start Guide

Get your MCP Gateway up and running in under 5 minutes! 🚀

---

## Prerequisites

- **Docker Desktop** (or Docker Engine + Docker Compose)
- **Python 3.9+** (optional, for tool_router MCP server)
- **Git** (to clone the repository)

---

## 🎯 Quick Setup (Copy & Paste)

### 1. Clone and Initialize

```bash
# Clone the repository
git clone https://github.com/LucasSantana-Dev/mcp-gateway.git
cd mcp-gateway

# Initialize the project
./scripts/mcp init

# Run health check
./scripts/mcp doctor
```

### 2. Start the Gateway

```bash
# Start all services
./scripts/mcp start

# Check status
./scripts/mcp status

# View logs (optional)
./scripts/mcp logs
```

### 3. Configure Your IDE

**For Windsurf:**
```bash
# Auto-detect and setup
./scripts/mcp ide setup

# Or generate config manually
./scripts/mcp ide config windsurf

# Restart Windsurf to activate
```

**For Cursor:**
```bash
./scripts/mcp ide config cursor
# Follow the instructions to add to Cursor settings
```

---

## 🎨 One-Line Setup (Advanced)

```bash
git clone https://github.com/LucasSantana-Dev/mcp-gateway.git && \
cd mcp-gateway && \
./scripts/mcp init && \
./scripts/mcp start && \
./scripts/mcp ide setup
```

---

## 🔧 Essential Commands

### Gateway Management
```bash
./scripts/mcp start      # Start gateway
./scripts/mcp stop       # Stop gateway
./scripts/mcp restart    # Restart gateway
./scripts/mcp status     # Check status
./scripts/mcp logs       # View all logs
./scripts/mcp logs gateway  # View specific service logs
```

### Server Management
```bash
./scripts/mcp server list              # List all servers
./scripts/mcp server enable brave-search   # Enable a server
./scripts/mcp server disable playwright    # Disable a server
./scripts/mcp server info context7         # Get server details
```

### Health & Diagnostics
```bash
./scripts/mcp doctor     # Run comprehensive health checks
```

### Shell Completion (Optional)
```bash
# Bash
./scripts/mcp completion bash >> ~/.bashrc
source ~/.bashrc

# Zsh
./scripts/mcp completion zsh >> ~/.zshrc
source ~/.zshrc

# Fish
./scripts/mcp completion fish > ~/.config/fish/completions/mcp.fish
```

---

## 🎯 What You Get

After setup, you'll have:

✅ **31 MCP Servers** ready to use:
- 🔍 Search: Brave, Exa, Tavily
- 🌐 Web: Fetch, Browser Tools, Playwright
- 💻 Development: GitHub, Git, Filesystem
- 🤖 AI: Context7, Sequential Thinking, Memory
- 📊 Data: Supabase, Postman, Snyk
- And many more!

✅ **Unified CLI** for easy management
✅ **IDE Integration** (Windsurf, Cursor)
✅ **Health Monitoring** with `mcp doctor`
✅ **Real-time Logs** with `mcp logs`

---

## 🚀 Next Steps

### Test Your Setup

**From your IDE (Windsurf/Cursor):**
```
"List all available MCP tools"
"Search for 'MCP best practices' using brave-search"
"Execute a task using the github server"
```

**From command line:**
```bash
# Test gateway health
curl http://localhost:4444/health

# View running services
docker compose ps

# Check logs for issues
./scripts/mcp logs
```

### Optimize Performance

```bash
# Disable unused servers to speed up startup
./scripts/mcp server disable browser-tools
./scripts/mcp server disable playwright
./scripts/mcp server disable chrome-devtools

# Restart to apply changes
./scripts/mcp restart

# Verify enabled servers
./scripts/mcp server list
```

### Customize Configuration

```bash
# Edit environment variables
nano .env

# Edit virtual servers
nano config/virtual-servers.txt

# Restart after changes
./scripts/mcp restart
```

---

## 🆘 Troubleshooting

### Gateway Won't Start

```bash
# Run diagnostics
./scripts/mcp doctor

# Check Docker is running
docker info

# View detailed logs
./scripts/mcp logs

# Reset and try again
./scripts/mcp stop
docker compose down -v
./scripts/mcp start
```

### IDE Not Connecting

```bash
# Verify configuration
./scripts/mcp ide detect

# Regenerate config
./scripts/mcp ide config windsurf

# Check tool_router is running
docker compose ps tool-router

# View tool_router logs
./scripts/mcp logs tool-router
```

### Slow Startup

```bash
# Disable unused servers
./scripts/mcp server list
./scripts/mcp server disable <server-name>

# Expected improvement: ~60% faster with selective loading
```

### Port Already in Use

```bash
# Check what's using port 4444
lsof -i :4444

# Stop conflicting service or change port in .env
echo "GATEWAY_PORT=5555" >> .env
./scripts/mcp restart
```

---

## 📚 Learn More

- **Full CLI Documentation**: `docs/cli/MCP_CLI.md`
- **Architecture Overview**: `PROJECT_CONTEXT.md`
- **API Documentation**: `docs/api/LIFECYCLE_API.md`
- **Configuration Guide**: `docs/configuration/`

---

## 💡 Pro Tips

1. **Use shell completion** for faster command entry
2. **Run `mcp doctor` regularly** to catch issues early
3. **Monitor logs** with `mcp logs -f` during development
4. **Disable unused servers** to optimize performance
5. **Use `mcp wizard`** for interactive setup

---

## 🎉 You're Ready!

Your MCP Gateway is now running and integrated with your IDE. Start building amazing AI-powered applications!

**Need help?**
- Check `./scripts/mcp help`
- Run `./scripts/mcp doctor`
- View logs with `./scripts/mcp logs`

Happy coding! 🚀
