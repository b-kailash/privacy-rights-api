# Source Control Setup — GitHub

**Repository:** github.com/b-kailash/privacy-rights-api

---

## Prerequisites

- Git installed locally (`git --version` to verify)
- GitHub CLI installed (`gh --version` to verify) — or use the GitHub web UI for Step 1
- GitHub account authenticated (`gh auth login` if using CLI)

If you don't have GitHub CLI:
```bash
# Install on Ubuntu/WSL
sudo apt install gh

# Authenticate
gh auth login
```

---

## Step 1: Create the Repository on GitHub

**Option A — Using GitHub CLI (recommended):**

```bash
cd ~/privacy-rights-api

gh repo create b-kailash/privacy-rights-api \
  --private \
  --description "GDPR/CCPA Data Subject Request Service — FastAPI microservice" \
  --source . \
  --push
```

> This creates the repo, initializes git locally, adds the remote, and pushes in one command. If this succeeds, skip to Step 5 (Verify).

**Option B — Using GitHub Web UI:**

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `privacy-rights-api`
   - **Description:** `GDPR/CCPA Data Subject Request Service — FastAPI microservice`
   - **Visibility:** Private (or Public if you prefer)
   - **Do NOT** initialize with README, .gitignore, or license (we already have files locally)
3. Click **Create repository**
4. Continue to Step 2

---

## Step 2: Initialize Local Git Repository

```bash
cd ~/privacy-rights-api

git init
```

---

## Step 3: Stage and Commit Existing Code

First, verify your `.gitignore` is in place so we don't commit `.venv/`, `__pycache__/`, etc.:

```bash
cat .gitignore
```

Should contain:
```
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.env
*.db
.ruff_cache/
```

Now stage and commit:

```bash
# Stage all files
git add .

# Verify what will be committed (make sure .venv is NOT listed)
git status

# Commit
git commit -m "Initial project scaffolding

- FastAPI application entry point (app/main.py)
- Project structure: app/api, app/core, app/middleware, app/models, app/schemas, app/services
- pyproject.toml with all dependencies
- pytest and ruff configuration
- .gitignore for Python/venv files"
```

---

## Step 4: Add Remote and Push

```bash
# Add the GitHub remote
git remote add origin git@github.com:b-kailash/privacy-rights-api.git

# Rename default branch to main (if not already)
git branch -M main

# Push and set upstream
git push -u origin main
```

> **Note:** If you use HTTPS instead of SSH, use this remote URL instead:
> `https://github.com/b-kailash/privacy-rights-api.git`

---

## Step 5: Verify

```bash
# Check remote is set
git remote -v

# Should show:
# origin  git@github.com:b-kailash/privacy-rights-api.git (fetch)
# origin  git@github.com:b-kailash/privacy-rights-api.git (push)

# Check status is clean
git status

# Should show: nothing to commit, working tree clean
```

Visit https://github.com/b-kailash/privacy-rights-api to confirm all files are visible.

---

## Step 6: Recommended Branch Strategy

For ongoing development, use feature branches per story:

```bash
# Create a feature branch for a story
git checkout -b feature/PB-005-config-management

# ... do work, commit ...

# Push the branch
git push -u origin feature/PB-005-config-management

# After peer review, merge to main
git checkout main
git pull
git merge feature/PB-005-config-management
git push

# Clean up
git branch -d feature/PB-005-config-management
```

**Branch naming convention:** `feature/PB-{id}-{short-description}`

---

## Quick Reference — Daily Workflow

```bash
# Check status
git status

# Stage specific files
git add app/core/config.py app/main.py

# Commit with descriptive message
git commit -m "PB-005: Add configuration management with pydantic-settings"

# Push to remote
git push
```
