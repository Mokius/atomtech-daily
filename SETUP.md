# ⚙️ Setup Guide — TechPulse Daily

Follow these steps once to activate the full automation.

---

## Step 1 — Create the GitHub Repository

```bash
# Option A: GitHub CLI
gh repo create techpulse-daily --public --description "Daily AI, engineering & science newsletter"

# Option B: Manual — go to https://github.com/new
```

---

## Step 2 — Push the Repository Structure

```bash
cd newsletter-repo

git init
git add .
git commit -m "feat: initialize TechPulse Daily newsletter repository"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/techpulse-daily.git
git push -u origin main
```

---

## Step 3 — Add GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from https://console.anthropic.com |

---

## Step 4 — Enable GitHub Actions

Go to your repo → **Actions** tab → Click "I understand my workflows, go ahead and enable them"

The workflow will now run automatically every day at **10:00 AM UTC**.

---

## Step 5 — Test Manually

Trigger a test run:
1. Go to **Actions → TechPulse Daily Newsletter**
2. Click **Run workflow**
3. Leave date blank (uses today)
4. Set `dry_run` to `true` for a test run without commits

---

## Step 6 — Configure Cowork Scheduled Task (Optional)

The Cowork scheduled task runs independently at 10:00 AM local time as a backup.
It was created automatically during setup. You can verify it in the Cowork task manager.

---

## Step 7 — Verify First Issue

After the first run:
```bash
ls issues/YYYY-MM-DD/
# Should show: newsletter.md  digest.md  social-posts.md  sources.md  index.md

git log --oneline -10
# Should show individual commits per file with professional messages
```

---

## Environment Variables (for local runs)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_REPO="username/techpulse-daily"

python scripts/generate_newsletter.py              # Today's issue
python scripts/generate_newsletter.py --dry-run    # Test without committing
python scripts/generate_newsletter.py --date 2026-04-28  # Specific date
python scripts/validate_issue.py --latest          # Validate last issue
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| API key error | Verify `ANTHROPIC_API_KEY` is set in GitHub Secrets |
| Git push fails | Check `GITHUB_TOKEN` permissions (needs `contents: write`) |
| Too few stories | Web search may have been rate limited — retry manually |
| Validation fails | Run `python scripts/validate_issue.py --latest` for details |
| Workflow not running | Check Actions is enabled; cron may delay up to 30 min |

---

*Questions? Open an issue in the repository.*
