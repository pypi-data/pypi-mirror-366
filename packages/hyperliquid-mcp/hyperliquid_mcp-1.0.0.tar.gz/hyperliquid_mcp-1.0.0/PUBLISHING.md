# 📦 Publishing Guide

Complete step-by-step guide to publish your Hyperliquid MCP server.

## 🚀 Quick Start

```bash
# Complete development setup
make dev

# When ready to release
make release
```

## 📋 Prerequisites Setup

### **GitHub Repository**
1. ✅ Already configured at: https://github.com/midodimori/hyperliquid-mcp
2. ✅ URLs already set in `pyproject.toml`
3. Push your code: `git push origin main`

### **PyPI Setup**
Choose one of these authentication methods:

#### **Option A: Trusted Publishing (Recommended)**
1. Create account at [PyPI.org](https://pypi.org/account/register/)
2. Go to https://pypi.org/manage/account/publishing/
3. Add GitHub repository as trusted publisher:
   - **Repository**: `midodimori/hyperliquid-mcp`
   - **Workflow**: `publish.yml` 
   - **Environment**: `pypi`
4. No API tokens needed! 🎉

#### **Option B: API Token**
1. Create account at [PyPI.org](https://pypi.org/account/register/)
2. Generate token: https://pypi.org/manage/account/token/
3. Set environment variable:
   ```bash
   export UV_PUBLISH_TOKEN=your_pypi_token
   ```

## 🎯 Simple Publishing Workflow

### **Step 1: Development**
```bash
make dev                        # Install deps, format code, run tests
```

### **Step 2: Release**
```bash
make release
# → Prompts for version (e.g., "0.1.0")
# → Runs tests and builds
# → Creates git tag and pushes to GitHub
```

### **Step 3: Create GitHub Release**
1. Go to: https://github.com/midodimori/hyperliquid-mcp/releases
2. Click "Create a new release"
3. Select the tag created by `make release` (e.g., `v0.1.0`)
4. Add release notes
5. Click "Publish release"

### **Step 4: Automatic Publishing**
🎉 **GitHub Actions automatically:**
- Tests on Ubuntu/macOS/Windows
- Builds the package
- Publishes to PyPI

## 📊 What Happens Where

| Action | Local (`make`) | GitHub Actions |
|--------|----------------|----------------|
| **Development** | `make dev` | Tests on PR/push |
| **Release Prep** | `make release` | - |
| **Publishing** | - | Auto on GitHub release |

## 🛠️ Available Commands

```bash
# Development
make help                       # See all commands
make dev                        # Complete setup (install + format + test)
make test                       # Run tests
make lint                       # Check code style
make clean                      # Clean build artifacts

# Release
make release                    # Full release process
make build                      # Build package only
```

## 🧪 Testing Installation

After publishing:

```bash
# Test your published package
uvx hyperliquid-mcp

# Alternative
pip install hyperliquid-mcp
```

## 🚨 Troubleshooting

### **Common Issues**

**Release fails with "working directory not clean"**
```bash
git status                      # Check what's uncommitted
git add . && git commit -m "Fix"  # Commit changes
make release                    # Try again
```

**Tests fail during release**
```bash
make test                       # Debug locally first
make lint                       # Fix any style issues
make release                    # Retry
```

**GitHub Actions fails**
- Check https://github.com/midodimori/hyperliquid-mcp/actions
- Ensure PyPI trusted publishing is set up correctly
- Verify repository settings match PyPI configuration

**Package already exists on PyPI**
- You're trying to upload a version that already exists
- Use a new version number in `make release`

## 📈 Version Management

Follow [Semantic Versioning](https://semver.org/):

- **`0.1.0`** - Initial release
- **`0.1.1`** - Bug fixes  
- **`0.2.0`** - New features
- **`1.0.0`** - Stable API

Example release progression:
```bash
make release  # → 0.1.0 (initial)
make release  # → 0.1.1 (bug fixes)
make release  # → 0.2.0 (new tools)
make release  # → 1.0.0 (stable)
```

## 🎉 Post-Publishing

After successful release:

1. ✅ Verify: https://pypi.org/project/hyperliquid-mcp/
2. ✅ Test: `uvx hyperliquid-mcp`
3. ✅ Update README badges if needed
4. ✅ Share with the community!

## 🔗 Resources

- **Your Package**: https://pypi.org/project/hyperliquid-mcp/
- **Repository**: https://github.com/midodimori/hyperliquid-mcp
- **Releases**: https://github.com/midodimori/hyperliquid-mcp/releases
- **Actions**: https://github.com/midodimori/hyperliquid-mcp/actions

---

**The simplified workflow:** `make dev` → `make release` → Create GitHub release → Auto-publish! 🚀