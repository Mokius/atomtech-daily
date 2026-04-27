#!/usr/bin/env python3
"""
TechPulse Daily — Issue Validator
==================================
Run before pushing. Checks structure, content quality, and formatting.

Usage:
    python validate_issue.py YYYY-MM-DD
    python validate_issue.py --latest
"""

import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
ISSUES_DIR = REPO_ROOT / "issues"
REQUIRED_FILES = ["newsletter.md", "digest.md", "social-posts.md", "sources.md", "index.md"]
MIN_NEWSLETTER_CHARS = 5000
MIN_ITEMS = 18


def check_file_exists(issue_dir: Path) -> list[str]:
    errors = []
    for f in REQUIRED_FILES:
        if not (issue_dir / f).exists():
            errors.append(f"Missing file: {f}")
    return errors


def check_newsletter_structure(content: str) -> list[str]:
    errors = []
    warnings = []

    # Must have a title
    if not content.startswith("# 🤖 TechPulse Daily"):
        errors.append("newsletter.md: Missing title header")

    # Count story sections (### N. emoji headline)
    story_count = len(re.findall(r"^### \d+\.", content, re.MULTILINE))
    if story_count < MIN_ITEMS:
        errors.append(f"newsletter.md: Only {story_count} stories (min {MIN_ITEMS})")

    # Check required sections in each story
    required_fields = ["**Summary**", "**Why It Matters**", "**What Is This?**",
                       "**Looking Ahead**", "**📱 Social Angle:**"]
    for field in required_fields:
        count = content.count(field)
        if count < MIN_ITEMS:
            warnings.append(f"newsletter.md: Field '{field}' appears only {count}x")

    # Check for placeholder text
    for placeholder in ["{{", "}}", "PLACEHOLDER", "TODO", "TBD"]:
        if placeholder in content:
            errors.append(f"newsletter.md: Contains unfilled placeholder '{placeholder}'")

    # Check minimum length
    if len(content) < MIN_NEWSLETTER_CHARS:
        errors.append(f"newsletter.md: Too short ({len(content)} chars, min {MIN_NEWSLETTER_CHARS})")

    return errors + [f"WARN: {w}" for w in warnings]


def check_sources(content: str) -> list[str]:
    errors = []
    urls = re.findall(r'https?://[^\s\)]+', content)
    if len(urls) < MIN_ITEMS:
        errors.append(f"sources.md: Only {len(urls)} URLs (expected ≥{MIN_ITEMS})")

    for url in urls:
        if not url.startswith("https://") and not url.startswith("http://"):
            errors.append(f"sources.md: Invalid URL: {url}")

    return errors


def check_duplicates(content: str) -> list[str]:
    errors = []
    headlines = re.findall(r"^### \d+\. [^\n]+", content, re.MULTILINE)
    seen = set()
    for h in headlines:
        normalized = h.lower().strip()
        if normalized in seen:
            errors.append(f"newsletter.md: Duplicate story: {h[:70]}")
        seen.add(normalized)
    return errors


def check_no_exaggeration(content: str) -> list[str]:
    """Soft check for common exaggeration patterns."""
    warnings = []
    patterns = [
        r"\bgroundbreaking\b", r"\brevolutionary\b", r"\bgame.changing\b",
        r"\bunprecedented\b", r"\bworld.changing\b", r"\bhistoric\b",
    ]
    for p in patterns:
        matches = re.findall(p, content, re.IGNORECASE)
        if len(matches) > 3:
            warnings.append(f"Overuse of superlative '{p}' ({len(matches)}x) — consider toning down")
    return [f"WARN: {w}" for w in warnings]


def validate_issue(date: str) -> bool:
    issue_dir = ISSUES_DIR / date
    if not issue_dir.exists():
        print(f"[ERROR] Issue directory not found: {issue_dir}")
        return False

    all_issues = []

    # 1. File existence
    all_issues.extend(check_file_exists(issue_dir))

    # 2. Newsletter structure
    newsletter_path = issue_dir / "newsletter.md"
    if newsletter_path.exists():
        content = newsletter_path.read_text(encoding="utf-8")
        all_issues.extend(check_newsletter_structure(content))
        all_issues.extend(check_duplicates(content))
        all_issues.extend(check_no_exaggeration(content))

    # 3. Sources
    sources_path = issue_dir / "sources.md"
    if sources_path.exists():
        sources_content = sources_path.read_text(encoding="utf-8")
        all_issues.extend(check_sources(sources_content))

    # 4. Digest
    digest_path = issue_dir / "digest.md"
    if digest_path.exists():
        digest_content = digest_path.read_text(encoding="utf-8")
        if len(digest_content) < 500:
            all_issues.append("digest.md: Too short (<500 chars)")

    errors = [i for i in all_issues if not i.startswith("WARN:")]
    warnings = [i for i in all_issues if i.startswith("WARN:")]

    print(f"\n{'='*50}")
    print(f"  Validation Report — {date}")
    print(f"{'='*50}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} Warning(s):")
        for w in warnings:
            print(f"   {w}")

    if errors:
        print(f"\n❌ {len(errors)} Error(s):")
        for e in errors:
            print(f"   {e}")
        print(f"\n✖  VALIDATION FAILED — do not push")
        return False
    else:
        print(f"\n✅ VALIDATION PASSED — safe to push")
        print(f"   Files: {len(REQUIRED_FILES)} | Warnings: {len(warnings)}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Validate a TechPulse Daily issue")
    parser.add_argument("date", nargs="?", help="Issue date (YYYY-MM-DD)")
    parser.add_argument("--latest", action="store_true", help="Validate the most recent issue")
    args = parser.parse_args()

    if args.latest:
        issues = sorted(ISSUES_DIR.glob("????-??-??"))
        if not issues:
            print("[ERROR] No issues found")
            sys.exit(1)
        date = issues[-1].name
    elif args.date:
        date = args.date
    else:
        date = datetime.now().strftime("%Y-%m-%d")

    success = validate_issue(date)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
