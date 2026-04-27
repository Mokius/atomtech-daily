#!/usr/bin/env python3
"""
TechPulse Daily — Newsletter Generation Script
===============================================
Runs daily at 10:00 AM.

Structure per issue:
  issues/YYYY-MM-DD/
    items/              ← ONE FILE + ONE COMMIT per news story
      01-ai-gpt55.md
      02-ai-deepseek-v4.md
      ...
    newsletter.md       ← Full newsletter (20 items grouped in 5 sections)
    digest.md           ← TL;DR
    social-posts.md     ← All social content aggregated
    sources.md          ← Source table
    index.md            ← Metadata

Commit strategy:
  news(ai): add GPT-5.5 release summary          ← per item
  news(security): add Defender zero-day report   ← per item
  ...
  daily: add YYYY-MM-DD full newsletter          ← aggregate
  daily: update YYYY-MM-DD index                 ← aggregate

Usage:
    python generate_newsletter.py [--date YYYY-MM-DD] [--dry-run] [--no-push]

Env vars:
    ANTHROPIC_API_KEY
    GITHUB_REPO   e.g. "Mokius/techpulse-daily"
"""

import os, sys, json, time, re, hashlib, argparse, subprocess
from datetime import datetime, timedelta
from pathlib import Path

import anthropic

REPO_ROOT   = Path(__file__).parent.parent
ISSUES_DIR  = REPO_ROOT / "issues"
MIN_ITEMS   = 18
MAX_ITEMS   = 25

SECTIONS = [
    ("ai_research",   "🤖 AI & Machine Learning",      ["ai", "research"]),
    ("engineering",   "💻 Engineering & Dev Tools",     ["engineering", "devtools"]),
    ("science_hw",    "🔬 Science & Hardware",          ["science", "hardware"]),
    ("security",      "🔐 Security & Infrastructure",   ["security", "cloud"]),
    ("startups",      "🚀 Startups, Robotics & More",   ["startups", "robotics"]),
]

CATEGORY_EMOJI = {
    "ai": "🤖", "research": "📄", "engineering": "💻",
    "devtools": "🛠️", "science": "🔬", "hardware": "💾",
    "security": "🔐", "cloud": "☁️", "startups": "🚀", "robotics": "🦾",
}

BLOCKLIST = [
    "click here", "you won't believe", "shocking", "insane",
    "mind-blowing", "epic fail", "viral", "top 10 reasons",
]


# ── helpers ──────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}", flush=True)

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:50]

def run_git(args, cwd=REPO_ROOT):
    return subprocess.run(["git"] + args, cwd=cwd,
                          capture_output=True, text=True, check=True)

def commit_file(path: Path, message: str):
    try:
        run_git(["add", str(path)])
        run_git(["commit", "-m", message])
        log(f"  ✔ {message}")
    except subprocess.CalledProcessError as e:
        log(f"  ↷ skip (nothing to commit): {e.stderr.strip()}", "WARN")

def get_issue_number():
    if not ISSUES_DIR.exists():
        return 1
    return len(sorted(ISSUES_DIR.glob("????-??-??"))) + 1

def deduplicate(items):
    seen, out = set(), []
    for item in items:
        key = hashlib.md5(item["headline"].lower().strip().encode()).hexdigest()
        if key not in seen:
            seen.add(key); out.append(item)
        else:
            log(f"  dup removed: {item['headline'][:50]}", "WARN")
    return out

def quality_check(items):
    issues = []
    if len(items) < MIN_ITEMS: issues.append(f"Too few items: {len(items)}")
    if len(items) > MAX_ITEMS: issues.append(f"Too many items: {len(items)}")
    required = ["headline","summary","why_it_matters","concept","future_impact",
                "source_url","category","hook","instagram_caption","hashtags",
                "linkedin_post","twitter_post"]
    for i, item in enumerate(items, 1):
        missing = [f for f in required if not item.get(f)]
        if missing: issues.append(f"Item {i} missing: {missing}")
        if not item.get("source_url","").startswith("http"):
            issues.append(f"Item {i} bad URL: {item.get('source_url','')}")
        h = item.get("headline","").lower()
        if any(p in h for p in BLOCKLIST):
            issues.append(f"Item {i} clickbait: {item['headline'][:50]}")
    return len(issues) == 0, issues


# ── news fetching ─────────────────────────────────────────────────────────────

def fetch_news(client, date):
    log("Fetching news via web search…")
    yesterday = (datetime.fromisoformat(date) - timedelta(days=1)).strftime("%Y-%m-%d")
    prompt = f"""You are a research assistant collecting technology news published between {yesterday} and {date}.

Search for the most important stories across:
- AI / Machine Learning (new models, agents, safety, research papers)
- Software Engineering (tools, frameworks, open source)
- Robotics (new robots, embodied AI, automation)
- Science (physics, biology, space, medicine)
- Developer Tools (IDEs, APIs, CLIs)
- Cybersecurity (vulnerabilities, breaches, defenses)
- Cloud & Infrastructure (AWS, GCP, Azure, Kubernetes)
- Hardware (chips, GPUs, quantum)
- Startups & Products (launches, funding)

For each story:
HEADLINE: exact title
URL: full source URL
DOMAIN: domain.com
DATE: publication date
CATEGORY: ai|engineering|robotics|science|devtools|security|cloud|hardware|startups|research
BRIEF: 2-3 sentence description

Find 25-30 stories from authoritative sources only.
Exclude clickbait, duplicates, low-quality content."""

    msg = client.messages.create(
        model="claude-opus-4-5", max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "\n".join(b.text for b in msg.content if hasattr(b, "text"))
    log(f"  ↳ {len(raw)} chars collected")
    return raw


# ── content generation ────────────────────────────────────────────────────────

def generate_items(client, raw_news, date):
    log("Generating structured items with per-item social content…")
    prompt = f"""You are a professional technology newsletter editor. Today is {date}.

Source material:
---
{raw_news}
---

Generate exactly 20 newsletter items. Each item must be a JSON object with these exact fields:

{{
  "headline": "Clear, professional, factual headline",
  "category": "ai|engineering|robotics|science|devtools|security|cloud|hardware|startups|research",
  "category_label": "Human-readable label with emoji e.g. 🤖 Artificial Intelligence",
  "impact_level": "🔴 High | 🟡 Medium | 🟢 Notable",
  "summary": "2-3 factual sentences describing what happened",
  "why_it_matters": "2-3 sentences on significance and implications",
  "concept": "1-2 plain-English sentences for a non-technical reader",
  "future_impact": "1-2 sentences on what this leads to",
  "source_url": "Full verified https:// URL",
  "source_name": "Publication name",
  "source_domain": "domain.com",

  // ── INDIVIDUAL SOCIAL CONTENT (self-contained per item) ──
  "hook": "One punchy opening line for Instagram (no hashtags)",
  "instagram_caption": "Full Instagram caption: hook + 4-6 short lines + call to action. Max 300 chars. Conversational, educational tone. No hashtags here.",
  "hashtags": "#AI #TechNews #[CategoryTag] #TechPulseDaily (6-8 relevant hashtags)",
  "linkedin_post": "150-200 word professional LinkedIn post. Headline + context + why it matters + question to audience.",
  "twitter_post": "Tweet thread: 3 tweets numbered 1/ 2/ 3/. Each under 280 chars. Include source URL in last tweet."
}}

Rules:
- Every field must be populated — no empty strings
- instagram_caption must be self-contained (readable without knowing anything else)
- linkedin_post must be self-contained
- twitter_post must be self-contained
- No duplicate stories
- No clickbait headlines
- Aim for 2 items per category
- Source URLs must be real and complete

Return ONLY a valid JSON array of 20 items. No markdown, no commentary."""

    msg = client.messages.create(
        model="claude-opus-4-5", max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"): raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):   raw = "\n".join(raw.split("\n")[:-1])
    items = json.loads(raw)
    log(f"  ↳ {len(items)} items generated")
    return items


# ── individual item file builder ──────────────────────────────────────────────

def build_item_md(item, item_number, date, section_label):
    emoji = CATEGORY_EMOJI.get(item["category"], "📌")
    return f"""---
title: "{item['headline'].replace('"', "'")}"
date: {date}
category: {item['category']}
category_label: "{item.get('category_label', item['category'])}"
impact: {item.get('impact_level', '🟡 Medium')}
source_url: {item['source_url']}
source_name: "{item.get('source_name', item.get('source_domain', 'Source'))}"
item_number: {item_number}
section: "{section_label}"
---

# {emoji} {item['headline']}

> **{item.get('category_label', item['category'])}** · {item.get('impact_level', '🟡 Medium')} · {date}

---

## 📋 Summary
{item['summary']}

## 💡 Why It Matters
{item['why_it_matters']}

## 🔍 What Is This?
{item['concept']}

## 🔭 Looking Ahead
{item['future_impact']}

---

## 📱 Instagram Slide

**Hook:**
{item['hook']}

**Caption:**
{item['instagram_caption']}

**Hashtags:**
{item['hashtags']}

---

## 💼 LinkedIn Post
{item['linkedin_post']}

---

## 🐦 Twitter / X
{item['twitter_post']}

---

**Source:** [{item.get('source_name', item.get('source_domain', 'Source'))}]({item['source_url']})
*TechPulse Daily · {date} · Item {item_number}/20*
"""


# ── aggregate file builders ───────────────────────────────────────────────────

def build_newsletter_md(items, date, issue_num):
    dt = datetime.fromisoformat(date)
    lines = [
        f"# 🤖 TechPulse Daily — {date}",
        "",
        f"> *Daily briefing on AI, engineering, science & technology — 20 stories · Issue #{issue_num}*",
        "",
        f"**{dt.strftime('%A, %B %d, %Y')}**",
        "",
        "---",
        "",
        "## 🗂️ Sections",
        "",
    ]
    for _, label, _ in SECTIONS:
        lines.append(f"- [{label}](#{slugify(label)})")
    lines += ["", "---", ""]

    # Group items by section
    section_items = {cats[0]: [] for _, _, cats in SECTIONS}
    assigned = set()
    for _, _, cats in SECTIONS:
        for item in items:
            if item["category"] in cats and id(item) not in assigned:
                section_items[cats[0]].append(item)
                assigned.add(id(item))
    # Remaining items go to last section
    for item in items:
        if id(item) not in assigned:
            section_items[SECTIONS[-1][2][0]].append(item)
            assigned.add(id(item))

    item_counter = 1
    for sec_key, sec_label, sec_cats in SECTIONS:
        lines += [f"## {sec_label}", ""]
        sec_items = section_items.get(sec_key, [])
        for item in sec_items:
            emoji = CATEGORY_EMOJI.get(item["category"], "📌")
            slug = f"{item_counter:02d}-{item['category']}-{slugify(item['headline'])}"
            lines += [
                f"### {item_counter}. {emoji} {item['headline']}",
                "",
                f"**Category:** `{item.get('category_label', item['category'])}` | "
                f"**Impact:** {item.get('impact_level','🟡 Medium')} | "
                f"**Source:** [{item.get('source_name','Source')}]({item['source_url']}) | "
                f"[📄 Full slide](./items/{slug}.md)",
                "",
                f"**Summary:** {item['summary']}",
                "",
                f"**Why It Matters:** {item['why_it_matters']}",
                "",
                f"**📱 Hook:** *{item['hook']}*",
                "",
                "---",
                "",
            ]
            item_counter += 1
        lines += [""]

    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    lines += [
        "## 📊 Stats",
        "",
        f"| Stories | {len(items)} |",
        "|---------|---|",
        f"| Sections | {len(SECTIONS)} |",
        f"| Generated | {now} |",
        "",
        "---",
        "*TechPulse Daily — automated, real timestamps, real sources.*",
    ]
    return "\n".join(lines)


def build_digest_md(items, date):
    lines = [
        f"# ⚡ TechPulse Digest — {date}",
        "",
        f"*{len(items)}-story quick read · [Full newsletter](./newsletter.md)*",
        "",
        "---",
        "",
    ]
    for i, item in enumerate(items, 1):
        slug = f"{i:02d}-{item['category']}-{slugify(item['headline'])}"
        lines.append(
            f"**{i}.** [{item['headline']}](./items/{slug}.md) "
            f"{item.get('impact_level','🟡')} — "
            f"*{item['summary'].split('.')[0]}.*"
        )
        lines.append("")
    lines += ["---", "", f"*→ [Full newsletter](./newsletter.md) | [Sources](./sources.md)*"]
    return "\n".join(lines)


def build_social_md(items, date):
    """Aggregated social file — each item links to its individual slide file."""
    lines = [
        f"# 📱 Social Posts — {date}",
        "",
        "*Each story has its own full slide file in `items/`. This is the quick-reference index.*",
        "",
        "---",
        "",
    ]
    for i, item in enumerate(items, 1):
        slug = f"{i:02d}-{item['category']}-{slugify(item['headline'])}"
        emoji = CATEGORY_EMOJI.get(item["category"], "📌")
        lines += [
            f"## {i}. {emoji} {item['headline']}",
            "",
            f"**[→ Full slide file](./items/{slug}.md)**",
            "",
            f"**Hook:** {item['hook']}",
            "",
            f"**Hashtags:** {item['hashtags']}",
            "",
            "---",
            "",
        ]
    lines += [f"*Generated by TechPulse Daily · {date}*"]
    return "\n".join(lines)


def build_sources_md(items, date):
    lines = [
        f"# 🔗 Sources — {date}",
        "",
        f"| # | Headline | Domain | Category |",
        "|---|----------|--------|----------|",
    ]
    for i, item in enumerate(items, 1):
        domain = item.get("source_domain", "—")
        title  = item["headline"][:55] + ("…" if len(item["headline"]) > 55 else "")
        lines.append(f"| {i} | [{title}]({item['source_url']}) | {domain} | {item['category']} |")
    lines += ["", f"*Fetched at {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"]
    return "\n".join(lines)


def build_index_md(items, date, issue_num, exec_time):
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    prev = (datetime.fromisoformat(date) - timedelta(days=1)).strftime("%Y-%m-%d")
    nxt  = (datetime.fromisoformat(date) + timedelta(days=1)).strftime("%Y-%m-%d")

    cat_counts: dict = {}
    for item in items:
        lbl = item.get("category_label", item["category"])
        cat_counts[lbl] = cat_counts.get(lbl, 0) + 1

    cat_rows = "\n".join(
        f"| {k} | {v} |" for k, v in cat_counts.items()
    )

    item_links = "\n".join(
        f"| {i:02d} | [{item['headline'][:55]}](./items/{i:02d}-{item['category']}-{slugify(item['headline'])}.md) | {item.get('category_label', item['category'])} |"
        for i, item in enumerate(items, 1)
    )

    return f"""# 📋 Index — {date}

**Issue #{issue_num} · Generated: {now}**

---

## All Items (20 individual slide files)

| # | Headline | Category |
|---|----------|----------|
{item_links}

---

## Category Breakdown

| Category | Count |
|----------|-------|
{cat_rows}

---

## Files

| File | Description |
|------|-------------|
| [newsletter.md](./newsletter.md) | Full newsletter — 5 sections, 20 stories |
| [digest.md](./digest.md) | One-line digest |
| [social-posts.md](./social-posts.md) | Social index (links to item slides) |
| [sources.md](./sources.md) | All {len(items)} sources |
| [items/](./items/) | **{len(items)} individual story + slide files** |

---

## Metadata

```yaml
date: {date}
issue_number: {issue_num}
generated_at: {now}
exec_time: {exec_time:.1f}s
item_count: {len(items)}
individual_slides: {len(items)}
categories: {len(cat_counts)}
```

*← [Previous]({prev}/index.md) | [All Issues](../../issues/) | [Next]({nxt}/index.md) →*
"""


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date",     default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--no-push",  action="store_true")
    args = parser.parse_args()

    date  = args.date
    t0    = time.time()
    log(f"═══ TechPulse Daily — {date} ═══")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log("ANTHROPIC_API_KEY not set", "ERROR"); sys.exit(1)

    client    = anthropic.Anthropic(api_key=api_key)
    issue_num = get_issue_number()
    issue_dir = ISSUES_DIR / date
    items_dir = issue_dir / "items"
    items_dir.mkdir(parents=True, exist_ok=True)
    log(f"Issue #{issue_num} → {issue_dir}")

    # ── 1. Fetch news ──
    raw_news = fetch_news(client, date)

    # ── 2. Generate structured items ──
    items = generate_items(client, raw_news, date)
    items = deduplicate(items)

    # ── 3. Quality check ──
    passed, qc_issues = quality_check(items)
    if not passed:
        for i in qc_issues: log(f"  QC: {i}", "ERROR")
        if not args.dry_run: sys.exit(1)
    else:
        log(f"Quality check passed ({len(items)} items)")

    # ── 4. Assign sections ──
    section_map: dict = {}
    assigned = set()
    for sec_key, sec_label, sec_cats in SECTIONS:
        for item in items:
            if item["category"] in sec_cats and id(item) not in assigned:
                section_map[id(item)] = sec_label
                assigned.add(id(item))
    for item in items:
        if id(item) not in assigned:
            section_map[id(item)] = SECTIONS[-1][1]

    exec_time = time.time() - t0

    # ── 5. Write & commit individual item files (one per story) ──
    log("Writing individual item files…")
    for i, item in enumerate(items, 1):
        sec_label = section_map[id(item)]
        slug      = f"{i:02d}-{item['category']}-{slugify(item['headline'])}"
        path      = items_dir / f"{slug}.md"
        path.write_text(build_item_md(item, i, date, sec_label), encoding="utf-8")

        if not args.dry_run:
            cat   = item["category"]
            title = item["headline"][:60]
            commit_file(path, f"news({cat}): {title}")

    # ── 6. Write & commit aggregate files ──
    log("Writing aggregate files…")
    agg_files = {
        "newsletter.md":   build_newsletter_md(items, date, issue_num),
        "digest.md":       build_digest_md(items, date),
        "social-posts.md": build_social_md(items, date),
        "sources.md":      build_sources_md(items, date),
        "index.md":        build_index_md(items, date, issue_num, exec_time),
    }
    agg_messages = {
        "newsletter.md":   f"daily: add {date} full newsletter ({len(items)} stories, 5 sections)",
        "digest.md":       f"daily: add {date} digest version",
        "social-posts.md": f"daily: add {date} social posts index",
        "sources.md":      f"daily: add {date} source references",
        "index.md":        f"daily: update {date} newsletter index",
    }
    for fname, content in agg_files.items():
        path = issue_dir / fname
        path.write_text(content, encoding="utf-8")
        if not args.dry_run:
            commit_file(path, agg_messages[fname])

    # ── 7. Push ──
    if not args.dry_run and not args.no_push:
        log("Pushing to GitHub…")
        try:
            run_git(["push", "origin", "main"])
            log("  ✔ Push successful")
        except subprocess.CalledProcessError as e:
            log(f"  ✘ Push failed: {e.stderr}", "ERROR"); raise

    elapsed = time.time() - t0
    log(f"═══ Done in {elapsed:.1f}s · Issue #{issue_num} · {len(items)} items · {len(items)} individual slides ═══")


if __name__ == "__main__":
    main()
