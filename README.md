# duckduckgo_mcp

A GitHub Actions workflow that auto-deploys to **Render** whenever a tag is pushed to any branch.

---

## 🚀 How It Works

```
git tag v1.0.0          →  GitHub detects tag push
                        →  GitHub Actions workflow runs
                        →  Render Deploy Hook is called
                        →  Render starts deployment ✅
```

---

## ⚙️ Setup

### Step 1: Get your Render Deploy Hook URL

1. Go to your **Render Dashboard** → Select your service
2. Navigate to **Settings** → **Deploy Hook**
3. Copy the deploy hook URL  
   *(looks like: `https://api.render.com/deploy/srv-xxxx?key=yyyy`)*

### Step 2: Add the secret to GitHub

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Name: `RENDER_DEPLOY_HOOK_URL`
4. Value: paste your Render deploy hook URL
5. Click **Add secret**

### Step 3: Create & push a tag to deploy

```bash
# Create a tag on your current branch
git tag v1.0.0

# Push the tag to GitHub (triggers deployment)
git push origin v1.0.0
```

---

## 🏷️ Tag Naming Convention

| Tag Pattern | Example | Use Case |
|-------------|---------|----------|
| `v*.*.*`    | `v1.0.0` | Production release |
| `v*.*.*-beta` | `v1.0.0-beta` | Beta release |
| `v*.*.*-rc*`  | `v1.0.0-rc1` | Release candidate |

All of the above trigger the workflow automatically.

---

## 📋 Workflow Logs

After pushing a tag:
1. Go to your GitHub repo → **Actions** tab
2. Click on the latest **"Deploy to Render on Tag"** run
3. View step-by-step logs and the deployment summary

---

## 🔐 Required GitHub PAT Scopes (for MCP testing)

| Scope | Purpose |
|-------|---------|
| `repo` | Push tags, read repo |
| `workflow` | Trigger & view workflow runs |
