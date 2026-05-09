# 🤖 AtomTech Daily — AI, Engineering & Science Newsletter

> **A fully automated daily newsletter covering the most relevant developments in AI, software engineering, robotics, scientific breakthroughs, developer tools, cybersecurity, cloud infrastructure, hardware, and startups.**

[![Daily Newsletter](https://img.shields.io/badge/cadence-daily-blue)](./issues/)
[![Automated](https://img.shields.io/badge/automation-GitHub%20Actions-green)](./github/workflows/)
[![Topics](https://img.shields.io/badge/topics-10%20categories-orange)](#categories)

---

## 📖 What Is This?

**AtomTech Daily** is a real-time, automatically generated newsletter repository. Every day at **10:00 AM**, a scheduled workflow:

1. Searches the web for the last 24 hours of news across 10 technology categories
2. Filters and ranks stories by relevance, impact, and credibility
3. Generates professional newsletter content with explanations, context, and social media angles
4. Commits every meaningful content update as a real, timestamped Git commit
5. Pushes the full issue to this repository

No fake timestamps. No backdated commits. Every commit represents a real execution.

---

## 📁 Repository Structure

```
newsletter-repo/
├── issues/                    # One folder per day
│   └── YYYY-MM-DD/
│       ├── newsletter.md      # Full newsletter (18–25 stories)
│       ├── digest.md          # Short TL;DR version
│       ├── social-posts.md    # Instagram / LinkedIn drafts
│       ├── sources.md         # All verified source links
│       └── index.md           # Day metadata and stats
├── articles/                  # Long-form individual articles
├── summaries/                 # Condensed weekly summaries
├── sources/                   # Global source registry
├── assets/                    # Images, banners, logos
├── templates/                 # Generation templates
├── .github/workflows/         # GitHub Actions automation
├── scripts/                   # Generation and validation scripts
├── README.md                  # This file
└── CHANGELOG.md               # Version history
```

---

## 🗂️ Categories

| # | Category | Description |
|---|----------|-------------|
| 1 | 🤖 Artificial Intelligence | Models, research, LLMs, agents, safety |
| 2 | 💻 Software Engineering | Languages, frameworks, architecture, OSS |
| 3 | 🦾 Robotics | Robots, automation, embodied AI |
| 4 | 🔬 Science | Breakthroughs in physics, bio, space, medicine |
| 5 | 🛠️ Developer Tools | IDEs, CLIs, APIs, productivity tools |
| 6 | 🔐 Cybersecurity | Vulnerabilities, exploits, defenses, privacy |
| 7 | ☁️ Cloud & Infrastructure | AWS, GCP, Azure, Kubernetes, DevOps |
| 8 | 💾 Hardware | Chips, GPUs, quantum, devices |
| 9 | 🚀 Startups & Products | Launches, funding rounds, pivots |
| 10 | 📄 Research Papers | Key preprints and published research |

---

## 🚀 How to Use This Repository

### Read the latest issue
Browse [`issues/`](./issues/) and open the most recent date folder.

### Subscribe to updates
Watch this repository (⭐ Star + 👁 Watch → "All Activity") to get GitHub notifications on each daily push.

### Reuse content
All content is structured for reuse:
- **Website**: Each `newsletter.md` is a self-contained Markdown page
- **Instagram**: Use `social-posts.md` for ready-to-post content
- **LinkedIn**: Adapt the "Why it matters" section from each item
- **Blog**: Expand any item using the "Concept explanation" section
- **Archive**: Every issue is immutable once committed — searchable forever

---

## ⚙️ Automation Stack

| Component | Technology |
|-----------|-----------|
| Scheduler | GitHub Actions (`cron: '0 10 * * *'`) + Cowork Task Scheduler |
| News Fetching | Web Search API (multi-source) |
| Content Generation | Claude AI (Anthropic) |
| Version Control | Git + GitHub |
| Validation | Python quality checks |
| Output Formats | Markdown (newsletter, digest, social, sources, index) |

---

## 🕐 Schedule

The workflow runs daily at **10:00 AM** (UTC for GitHub Actions, local time for Cowork scheduler).

Each run produces:
- ≥ 18 and ≤ 25 newsletter items
- All 5 output files per issue
- Multiple clean Git commits (one per meaningful content block)
- A push to the `main` branch

---

## 📜 Commit Convention

```
news: add summary on [topic]
science: add [discovery] analysis
engineering: add [tool/framework] update
ai: add [model/paper] summary
security: add [cve/breach] report
daily: update YYYY-MM-DD newsletter index
meta: update source registry
```

---

## 🤝 Contributing

This is an automated repository. To suggest sources or categories, open an Issue.

---

*Generated and maintained by TechPulse Daily Automation. All commit timestamps are real.*
