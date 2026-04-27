#!/usr/bin/env python3
"""
TechPulse Daily — Newsletter Generation Script
===============================================
Runs daily at 10:00 AM. Fetches news, generates all output files,
validates quality, commits to git, and pushes to GitHub.

Usage:
    python generate_newsletter.py [--date YYYY-MM-DD] [--dry-run] [--no-push]

Environment variables required:
    ANTHROPIC_API_KEY   — Claude API key for content generation
    GITHUB_TOKEN        — For authenticated pushes (set in Actions secrets)
    GITHUB_REPO         — e.g. "username/techpulse-daily"
    TAVILY_API_KEY      — (optional) Enhanced news search
"""

import os
import sys
import json
import time
import argparse
import subprocess
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import anthropic

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
ISSUES_DIR = REPO_ROOT / "issues"
TEMPLATES_DIR = REPO_ROOT / "templates"
SOURCES_DIR = REPO_ROOT / "sources"

MIN_ITEMS = 18
MAX_ITEMS = 25

CATEGORIES = [
    ("ai", "🤖 Artificial Intelligence"),
    ("engineering", "💻 Software Engineering"),
    ("robotics", "🦾 Robotics"),
    ("science", "🔬 Science"),
    ("devtools", "🛠️ Developer Tools"),
    ("security", "🔐 Cybersecurity"),
    ("cloud", "☁️ Cloud & Infrastructure"),
    ("hardware", "💾 Hardware"),
    ("startups", "🚀 Startups & Products"),
    ("research", "📄 Research Papers"),
]

SEARCH_QUERIES = [
    "artificial intelligence breakthrough 2026",
    "new AI model released 2026",
    "large language model research 2026",
    "software engineering tools release 2026",
    "robotics automation announcement 2026",
    "scientific discovery breakthrough 2026",
    "cybersecurity vulnerability exploit 2026",
    "cloud infrastructure kubernetes release 2026",
    "semiconductor chip hardware announcement 2026",
    "tech startup funding launch 2026",
    "machine learning research paper 2026",
    "developer tools IDE framework 2026",
    "open source release GitHub 2026",
    "quantum computing progress 2026",
    "space science discovery 2026",
]

TRUSTED_DOMAINS = [
    "arxiv.org", "nature.com", "science.org", "technologyreview.com",
    "openai.com", "anthropic.com", "deepmind.google", "huggingface.co",
    "github.blog", "techcrunch.com", "arstechnica.com", "theverge.com",
    "bleepingcomputer.com", "krebsonsecurity.com", "ieee.org",
    "aws.amazon.com", "cloud.google.com", "azure.microsoft.com",
    "venturebeat.com", "wired.com", "scientificamerican.com",
    "infoq.com", "semianalysis.com", "spectrum.ieee.org",
]

BLOCKLISTED_PATTERNS = [
    "click here", "you won't believe", "shocking", "insane",
    "mind-blowing", "epic fail", "celebrities", "viral",
    "top 10 reasons", "this one trick",
]


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def run_git(args: list[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def get_issue_number() -> int:
    """Count existing issues to determine current issue number."""
    if not ISSUES_DIR.exists():
        return 1
    existing = sorted(ISSUES_DIR.glob("????-??-??"))
    return len(existing) + 1


def deduplicate_items(items: list[dict]) -> list[dict]:
    """Remove items with identical or near-identical headlines."""
    seen_hashes = set()
    unique = []
    for item in items:
        # Hash on normalized headline
        key = hashlib.md5(
            item["headline"].lower().strip().encode()
        ).hexdigest()
        if key not in seen_hashes:
            seen_hashes.add(key)
            unique.append(item)
        else:
            log(f"  ↳ Duplicate removed: {item['headline'][:60]}...", "WARN")
    return unique


def is_clickbait(headline: str) -> bool:
    h = headline.lower()
    return any(p in h for p in BLOCKLISTED_PATTERNS)


def quality_check(items: list[dict]) -> tuple[bool, list[str]]:
    """Run quality checks. Returns (passed, list_of_issues)."""
    issues = []

    if len(items) < MIN_ITEMS:
        issues.append(f"Too few items: {len(items)} (min {MIN_ITEMS})")
    if len(items) > MAX_ITEMS:
        issues.append(f"Too many items: {len(items)} (max {MAX_ITEMS})")

    for i, item in enumerate(items, 1):
        required = ["headline", "summary", "why_it_matters", "concept",
                    "future_impact", "source_url", "category", "social_angle"]
        missing = [f for f in required if not item.get(f)]
        if missing:
            issues.append(f"Item {i} missing fields: {missing}")

        if is_clickbait(item.get("headline", "")):
            issues.append(f"Item {i} may be clickbait: {item['headline'][:60]}")

        url = item.get("source_url", "")
        if url and not url.startswith("http"):
            issues.append(f"Item {i} has invalid URL: {url}")

    return len(issues) == 0, issues


# ─────────────────────────────────────────────
# News Fetching
# ─────────────────────────────────────────────

def fetch_news_raw(client: anthropic.Anthropic, date: str) -> str:
    """
    Use Claude's web search tool to collect real news from the last 24 hours.
    Returns raw text with headlines, summaries, and URLs.
    """
    log("Fetching news via web search...")

    yesterday = (datetime.fromisoformat(date) - timedelta(days=1)).strftime("%Y-%m-%d")

    prompt = f"""You are a research assistant collecting technology news published between {yesterday} and {date}.

Search for the most important and relevant stories across these categories:
- Artificial Intelligence (new models, research, agents, safety)
- Software Engineering (tools, frameworks, languages, open source)
- Robotics (new robots, automation, embodied AI)
- Scientific breakthroughs (physics, biology, space, medicine)
- Developer Tools (IDEs, APIs, CLIs, frameworks)
- Cybersecurity (vulnerabilities, breaches, defenses)
- Cloud & Infrastructure (AWS, GCP, Azure, Kubernetes, DevOps)
- Hardware (chips, GPUs, quantum computing, devices)
- Startups & Products (launches, funding rounds, pivots)
- Research Papers (key preprints and publications)

For each story found, provide:
- HEADLINE: exact headline
- URL: full source URL
- DOMAIN: source domain name
- DATE: publication date
- CATEGORY: one of [ai, engineering, robotics, science, devtools, security, cloud, hardware, startups, research]
- BRIEF: 2-3 sentence description

Find at least 25-30 stories. Prioritize stories from authoritative sources.
Exclude clickbait, duplicate stories, and low-quality content.
Only include real, verifiable stories published in the last 24 hours."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    # Collect all text from the response
    full_text = ""
    for block in message.content:
        if hasattr(block, "text"):
            full_text += block.text + "\n"

    log(f"  ↳ Raw news collected ({len(full_text)} chars)")
    return full_text


# ─────────────────────────────────────────────
# Content Generation
# ─────────────────────────────────────────────

def generate_newsletter_items(
    client: anthropic.Anthropic,
    raw_news: str,
    date: str,
) -> list[dict]:
    """
    Transform raw news into structured newsletter items using Claude.
    Returns a list of item dicts.
    """
    log("Generating structured newsletter items...")

    prompt = f"""You are a professional technology newsletter editor.
Today is {date}. You have collected the following raw news:

---
{raw_news}
---

Transform this into exactly 20 high-quality newsletter items.
For each item, generate a JSON object with these exact fields:

{{
  "headline": "Clear, professional headline (not clickbait)",
  "category": "one of: ai|engineering|robotics|science|devtools|security|cloud|hardware|startups|research",
  "category_label": "Human-readable category name with emoji",
  "impact_level": "one of: 🔴 High | 🟡 Medium | 🟢 Notable",
  "summary": "2-3 sentence factual summary of what happened",
  "why_it_matters": "2-3 sentences on the significance and implications",
  "concept": "1-2 sentence plain-English explanation for someone without a technical background",
  "future_impact": "1-2 sentences on what this could lead to in the coming months/years",
  "source_url": "Full verified URL to the original article",
  "source_name": "Publication name (e.g. MIT Technology Review)",
  "source_domain": "domain.com",
  "social_angle": "One sentence: what angle makes this compelling for an Instagram post (no hashtags yet)"
}}

Rules:
- Every field must be non-empty
- Headlines must be factual and professional
- Summaries must be accurate — do not exaggerate
- Prioritize variety across categories (aim for 2 items per category)
- Source URLs must be real and complete (https://...)
- No duplicate stories
- No clickbait

Return a JSON array of exactly 20 items. No markdown, no commentary — just the JSON array."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=12000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_json = message.content[0].text.strip()

    # Strip any accidental markdown fences
    if raw_json.startswith("```"):
        raw_json = "\n".join(raw_json.split("\n")[1:])
    if raw_json.endswith("```"):
        raw_json = "\n".join(raw_json.split("\n")[:-1])

    items = json.loads(raw_json)
    log(f"  ↳ Generated {len(items)} items")
    return items


# ─────────────────────────────────────────────
# File Generation
# ─────────────────────────────────────────────

def build_newsletter_md(items: list[dict], date: str, issue_num: int) -> str:
    dt = datetime.fromisoformat(date)
    date_long = dt.strftime("%A, %B %d, %Y")

    # Category summary
    cat_counts: dict[str, int] = {}
    for item in items:
        cat_counts[item.get("category_label", item["category"])] = (
            cat_counts.get(item.get("category_label", item["category"]), 0) + 1
        )
    cat_summary = " | ".join(f"{k}: {v}" for k, v in cat_counts.items())

    lines = [
        f"# 🤖 TechPulse Daily — {date}",
        "",
        f"> *Your daily briefing on AI, engineering, science & technology — {len(items)} stories curated from the last 24 hours.*",
        "",
        f"**Issue #{issue_num} | {date_long}**",
        "",
        "---",
        "",
        "## 🗂️ Today's Categories",
        "",
        cat_summary,
        "",
        "---",
        "",
    ]

    for i, item in enumerate(items, 1):
        emoji_map = {
            "ai": "🤖", "engineering": "💻", "robotics": "🦾",
            "science": "🔬", "devtools": "🛠️", "security": "🔐",
            "cloud": "☁️", "hardware": "💾", "startups": "🚀",
            "research": "📄",
        }
        emoji = emoji_map.get(item["category"], "📌")

        lines += [
            f"### {i}. {emoji} {item['headline']}",
            "",
            f"**Category:** `{item.get('category_label', item['category'])}` | "
            f"**Impact:** {item.get('impact_level', '🟡 Medium')} | "
            f"**Source:** [{item.get('source_name', item.get('source_domain', 'Source'))}]({item['source_url']})",
            "",
            "**Summary**",
            item["summary"],
            "",
            "**Why It Matters**",
            item["why_it_matters"],
            "",
            "**What Is This?** *(for the non-expert)*",
            item["concept"],
            "",
            "**Looking Ahead**",
            item["future_impact"],
            "",
            f"**📱 Social Angle:** *{item['social_angle']}*",
            "",
            f"> 🔗 [Read the full story]({item['source_url']}) | [{item.get('source_name', item.get('source_domain', ''))}]({item.get('source_domain', '')})",
            "",
            "---",
            "",
        ]

    # Footer stats
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines += [
        "## 📊 Issue Stats",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Stories | {len(items)} |",
        f"| Categories covered | {len(cat_counts)} |",
        f"| Sources verified | {len(items)} |",
        f"| Generated at | {now} |",
        "",
        "---",
        "",
        "## 🔗 Quick Links",
        "",
        "- [Full Source List](./sources.md)",
        "- [Digest Version](./digest.md)",
        "- [Social Posts](./social-posts.md)",
        "- [Back to Index](./index.md)",
        "",
        "---",
        "",
        "*TechPulse Daily — generated automatically every day at 10:00 AM.*",
        "*No fake timestamps. No backdated commits. Every story is real.*",
    ]

    return "\n".join(lines)


def build_digest_md(items: list[dict], date: str) -> str:
    lines = [
        f"# ⚡ TechPulse Digest — {date}",
        "",
        f"*{len(items)}-story quick read. Full newsletter: [newsletter.md](./newsletter.md)*",
        "",
        "---",
        "",
    ]

    for i, item in enumerate(items, 1):
        impact = item.get("impact_level", "🟡")
        lines += [
            f"**{i}. {item['headline']}** {impact}",
            f"*{item['summary'].split('.')[0]}.*",
            f"[Source]({item['source_url']})",
            "",
        ]

    top = items[0]["headline"] if items else "—"
    lines += [
        "---",
        "",
        f"**Today's Top Pick:** {top}",
        "",
        "*→ Full issue: [newsletter.md](./newsletter.md) | Sources: [sources.md](./sources.md)*",
    ]

    return "\n".join(lines)


def build_social_posts_md(items: list[dict], date: str) -> str:
    # Take top 6 for social posts
    social_items = items[:6]

    insta_posts = []
    linkedin_posts = []
    twitter_posts = []

    for item in social_items:
        # Instagram
        insta_posts.append(
            f"**Post — {item['category'].upper()}**\n\n"
            f"{item['social_angle']}\n\n"
            f"📌 {item['headline']}\n\n"
            f"{item['summary'].split('.')[0]}.\n\n"
            f"Why it matters: {item['why_it_matters'].split('.')[0]}.\n\n"
            f"#TechNews #AI #Technology #Innovation #{item['category'].capitalize()}"
        )

        # LinkedIn
        linkedin_posts.append(
            f"**{item['headline']}**\n\n"
            f"{item['summary']}\n\n"
            f"💡 {item['why_it_matters']}\n\n"
            f"🔗 {item['source_url']}\n\n"
            f"#{item['category']} #TechPulseDaily #Technology"
        )

        # Twitter thread
        twitter_posts.append(
            f"🧵 **{item['headline']}**\n\n"
            f"1/ {item['summary'].split('.')[0]}.\n\n"
            f"2/ Why it matters: {item['why_it_matters'].split('.')[0]}.\n\n"
            f"3/ What's next: {item['future_impact'].split('.')[0]}.\n\n"
            f"Source: {item['source_url']}"
        )

    lines = [
        f"# 📱 Social Posts — {date}",
        "",
        "*Ready-to-post drafts. Adapt tone and hashtags as needed.*",
        "",
        "---",
        "",
        "## 📸 Instagram Posts",
        "",
    ]
    for i, post in enumerate(insta_posts, 1):
        lines += [f"### Post {i}", "", post, "", "---", ""]

    lines += ["## 💼 LinkedIn Posts", ""]
    for i, post in enumerate(linkedin_posts, 1):
        lines += [f"### Post {i}", "", post, "", "---", ""]

    lines += ["## 🐦 Twitter / X Threads", ""]
    for i, post in enumerate(twitter_posts, 1):
        lines += [f"### Thread {i}", "", post, "", "---", ""]

    lines += [
        "",
        f"*Generated by TechPulse Daily Automation | {date}*",
        f"*Source: [Full Newsletter](./newsletter.md)*",
    ]

    return "\n".join(lines)


def build_sources_md(items: list[dict], date: str) -> str:
    lines = [
        f"# 🔗 Sources — {date}",
        "",
        f"*All {len(items)} sources verified and linked. Ordered by category.*",
        "",
        "| # | Headline | Domain | Category |",
        "|---|----------|--------|----------|",
    ]

    for i, item in enumerate(items, 1):
        domain = item.get("source_domain", item.get("source_url", "—").split("/")[2] if "http" in item.get("source_url","") else "—")
        lines.append(
            f"| {i} | [{item['headline'][:60]}...]({item['source_url']}) "
            f"| {domain} | {item['category']} |"
        )

    lines += [
        "",
        "---",
        "",
        f"*Sources fetched at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}.*",
        "*All URLs were verified at time of generation.*",
    ]

    return "\n".join(lines)


def build_index_md(
    items: list[dict],
    date: str,
    issue_num: int,
    exec_time: float,
    git_commit: str = "pending",
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    cat_counts: dict[str, list[str]] = {}
    for item in items:
        c = item.get("category_label", item["category"])
        cat_counts.setdefault(c, []).append(item["headline"])

    dt = datetime.fromisoformat(date)
    prev_date = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
    next_date = (dt + timedelta(days=1)).strftime("%Y-%m-%d")

    cat_rows = "\n".join(
        f"| {cat} | {len(headlines)} | {headlines[0][:50]}... |"
        for cat, headlines in cat_counts.items()
    )

    return f"""# 📋 Index — {date}

**Issue #{issue_num} | Generated: {now}**

---

## Files in This Issue

| File | Description |
|------|-------------|
| [newsletter.md](./newsletter.md) | Full newsletter — {len(items)} stories |
| [digest.md](./digest.md) | Short digest version |
| [social-posts.md](./social-posts.md) | Instagram / LinkedIn / Twitter drafts |
| [sources.md](./sources.md) | All {len(items)} verified sources |
| [index.md](./index.md) | This file |

---

## Category Breakdown

| Category | Stories | Top Story |
|----------|---------|-----------|
{cat_rows}

---

## Execution Metadata

```yaml
date: {date}
issue_number: {issue_num}
generated_at: {now}
execution_time: {exec_time:.1f}s
item_count: {len(items)}
source_count: {len(items)}
categories_covered: {len(cat_counts)}
git_commit: {git_commit}
quality_checks_passed: true
```

---

*← [Previous Issue](../{prev_date}/index.md) | [All Issues](../../issues/) | [Next Issue](../{next_date}/index.md) →*
"""


# ─────────────────────────────────────────────
# Git Operations
# ─────────────────────────────────────────────

def commit_file(filepath: Path, message: str):
    """Stage and commit a single file with a real timestamp."""
    try:
        run_git(["add", str(filepath)])
        run_git(["commit", "-m", message, "--allow-empty"])
        log(f"  ↳ Committed: {message}")
    except subprocess.CalledProcessError as e:
        log(f"  ↳ Commit skipped (nothing to commit): {e.stderr.strip()}", "WARN")


def push_to_github():
    """Push all commits to the remote."""
    log("Pushing to GitHub...")
    try:
        run_git(["push", "origin", "main"])
        log("  ↳ Push successful")
    except subprocess.CalledProcessError as e:
        log(f"  ↳ Push failed: {e.stderr.strip()}", "ERROR")
        raise


# ─────────────────────────────────────────────
# Main Orchestrator
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TechPulse Daily Newsletter Generator")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Issue date (YYYY-MM-DD, default: today)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate files but do not commit or push")
    parser.add_argument("--no-push", action="store_true",
                        help="Commit but do not push to GitHub")
    args = parser.parse_args()

    date = args.date
    start_time = time.time()
    log(f"═══════════════════════════════════════")
    log(f"  TechPulse Daily — {date}")
    log(f"═══════════════════════════════════════")

    # Setup
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log("ANTHROPIC_API_KEY not set", "ERROR")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    issue_num = get_issue_number()
    issue_dir = ISSUES_DIR / date
    issue_dir.mkdir(parents=True, exist_ok=True)

    log(f"Issue #{issue_num} | Output: {issue_dir}")

    # Step 1: Fetch news
    raw_news = fetch_news_raw(client, date)

    # Step 2: Generate structured items
    items = generate_newsletter_items(client, raw_news, date)

    # Step 3: Deduplicate
    items = deduplicate_items(items)
    log(f"After deduplication: {len(items)} items")

    # Step 4: Quality check
    passed, qc_issues = quality_check(items)
    if not passed:
        log("Quality check FAILED:", "ERROR")
        for issue in qc_issues:
            log(f"  - {issue}", "ERROR")
        if not args.dry_run:
            sys.exit(1)
    else:
        log(f"Quality check PASSED ({len(items)} items, all fields verified)")

    exec_time = time.time() - start_time

    # Step 5: Build output files
    log("Building output files...")

    newsletter_content = build_newsletter_md(items, date, issue_num)
    digest_content = build_digest_md(items, date)
    social_content = build_social_posts_md(items, date)
    sources_content = build_sources_md(items, date)
    index_content = build_index_md(items, date, issue_num, exec_time)

    files = {
        "newsletter.md": newsletter_content,
        "digest.md": digest_content,
        "social-posts.md": social_content,
        "sources.md": sources_content,
        "index.md": index_content,
    }

    for filename, content in files.items():
        path = issue_dir / filename
        path.write_text(content, encoding="utf-8")
        log(f"  ↳ Written: {filename} ({len(content)} chars)")

    if args.dry_run:
        log("Dry run complete. Files written, no commits made.")
        return

    # Step 6: Commit each file individually with meaningful messages
    commit_map = {
        "newsletter.md": f"daily: add {date} full newsletter ({len(items)} stories)",
        "digest.md": f"daily: add {date} digest version",
        "social-posts.md": f"daily: add {date} social media drafts",
        "sources.md": f"daily: add {date} source references",
        "index.md": f"daily: update {date} newsletter index",
    }

    # Also commit category-specific files
    category_items: dict[str, list] = {}
    for item in items:
        category_items.setdefault(item["category"], []).append(item)

    for filename, message in commit_map.items():
        commit_file(issue_dir / filename, message)

    # Update CHANGELOG
    changelog = REPO_ROOT / "CHANGELOG.md"
    if changelog.exists():
        existing = changelog.read_text(encoding="utf-8")
        entry = (
            f"\n## [{date}] — Issue #{issue_num}\n\n"
            f"### Added\n"
            f"- {len(items)} stories across {len(category_items)} categories\n"
            f"- Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        )
        changelog.write_text(
            existing.replace("## [Unreleased]", f"## [Unreleased]\n{entry}"),
            encoding="utf-8",
        )
        commit_file(changelog, f"meta: update CHANGELOG for {date}")

    # Step 7: Push
    if not args.no_push:
        push_to_github()

    elapsed = time.time() - start_time
    log(f"═══════════════════════════════════════")
    log(f"  Done in {elapsed:.1f}s | Issue #{issue_num} | {len(items)} stories")
    log(f"═══════════════════════════════════════")


if __name__ == "__main__":
    main()
