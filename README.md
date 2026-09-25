# duckduckgo_mcp

A **DuckDuckGo Search MCP Server** with CI/CD — auto-deploys to **Render** whenever a version tag is pushed.

---

## 🗂️ Project Structure

```
├── server.py                      ← MCP server (4 tools)
├── render.yaml                    ← Render infrastructure config
├── requirements.txt
├── pyproject.toml
├── tests/
│   ├── conftest.py
│   └── test_server.py            ← 30 unit tests (98% coverage)
└── .github/workflows/
    └── deploy-on-tag.yml         ← CI: test → deploy on tag push
```

---

## 🛠️ MCP Tools

| Tool | Description | Key Params |
|------|-------------|------------|
| `search_web` | General web search | `query`, `max_results`, `region`, `safe_search` |
| `search_news` | Latest news articles | `query`, `max_results`, `time_filter` (d/w/m) |
| `search_images` | Image search | `query`, `size`, `color` |
| `search_videos` | Video search | `query`, `duration` (short/medium/long) |

---

## 🚀 How the CI/CD Works

```
Push tag v1.0.0
     ↓
GitHub Actions: run unit tests (Python 3.11 + 3.12)
     ↓ (only if tests pass)
Render Deploy Hook triggered
     ↓
Render pulls latest code → builds → starts server ✅
```

---

## ⚙️ Render Setup (One-time)

### Step 1 — Create the service on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repo: `soldierboyfather-cpu/duckduckgo_mcp`
3. Render auto-detects `render.yaml` — confirm settings:

| Setting | Value |
|---------|-------|
| **Name** | `duckduckgo-mcp` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python server.py` |
| **Plan** | Free |
| **Auto-Deploy** | ❌ Off (we deploy via GitHub Actions only) |

4. Click **Create Web Service**

---

### Step 2 — Get the Deploy Hook URL

1. In Render Dashboard → your service → **Settings**
2. Scroll to **Deploy Hook** section
3. Click **Generate Deploy Hook**
4. Copy the URL — looks like:
   ```
   https://api.render.com/deploy/srv-xxxxxxxx?key=yyyyyy
   ```

---

### Step 3 — Add Deploy Hook to GitHub Secrets

1. GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Set:
   - **Name**: `RENDER_DEPLOY_HOOK_URL`
   - **Value**: paste the Render hook URL
4. Click **Add secret**

---

## 🏷️ Deploy a New Version

```bash
# Create and push a version tag → triggers CI → deploys to Render
git tag v1.0.0
git push origin v1.0.0
```

### Tag naming convention

| Tag | Use case |
|-----|----------|
| `v1.0.0` | Production release |
| `v1.0.0-beta` | Beta / staging |
| `v1.0.0-rc1` | Release candidate |

---

## 🧪 Running Tests Locally

```bash
# Unit tests only (fast, no network)
pytest tests/ -m "not integration"

# Live integration tests (hits real DuckDuckGo API)
pytest tests/ -m integration -v

# With coverage report
pytest tests/ -m "not integration" --cov=server --cov-report=term-missing
```

---

## 🖥️ Running Locally as MCP Server

```bash
pip install -r requirements.txt

# stdio mode (for MCP clients like Claude Desktop)
python server.py

# HTTP mode (for testing the Render transport locally)
PORT=8000 python server.py
# → Server available at http://localhost:8000/mcp
```

### Claude Desktop config (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "duckduckgo": {
      "command": "python",
      "args": ["D:/workspace/duckduckgo_search/server.py"]
    }
  }
}
```

---

## 🔐 Required GitHub PAT Scopes

| Scope | Purpose |
|-------|---------|
| `repo` | Push tags, read commits |
| `workflow` | Trigger & view GitHub Actions |
