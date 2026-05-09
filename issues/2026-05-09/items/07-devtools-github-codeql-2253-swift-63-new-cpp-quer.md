---
title: "GitHub CodeQL 2.25.3 Released with Swift 6.3 Support and New C++ Security Queries"
date: 2026-05-09
category: devtools
category_label: "💻 Dev Tools"
impact: "🟡 Medium"
source_url: https://releasebot.io/updates/github
source_name: "Releasebot / GitHub"
item_number: 7
section: "💻 Engineering & Dev Tools"
---

# 💻 GitHub CodeQL 2.25.3 Released with Swift 6.3 Support and New C++ Security Queries

> **💻 Dev Tools** · 🟡 Medium · 2026-05-09

---

## 📋 Summary
GitHub released CodeQL 2.25.3, delivering Swift 6.3 support, five new default C/C++ security queries, and accuracy improvements across Python, Java/Kotlin, JavaScript, C#, and GitHub Actions analysis. CodeQL is GitHub's static analysis engine used in GitHub Advanced Security to automatically detect security vulnerabilities in source code. The C/C++ additions target memory safety and injection vulnerability patterns.

## 💡 Why It Matters
Static analysis tooling that keeps pace with language releases is critical for maintaining security coverage in modern codebases. Swift 6.3 support ensures mobile and server-side Swift projects benefit from automated vulnerability detection without manual rule updates. The five new C/C++ queries address vulnerability classes that are responsible for a significant share of critical CVEs in systems software — bringing automated detection of these patterns to all Advanced Security users.

## 🔍 What Is This?
CodeQL is a tool that treats code like data, letting you write queries that find security vulnerabilities across entire codebases. GitHub Advanced Security uses CodeQL queries to automatically flag potential vulnerabilities in pull requests and repositories. "Default queries" are the ones that run automatically for all repositories — making the new C/C++ additions particularly high-impact.

## 🔭 Looking Ahead
As language ecosystems evolve faster, keeping static analysis tooling current is an ongoing challenge. GitHub's cadence of CodeQL updates reflects a broader trend toward automated, continuous security coverage as part of the development workflow rather than periodic security audits.

---

## 📱 Instagram Slide

**Hook:**
CodeQL 2.25.3 drops — Swift 6.3 security analysis and 5 new C++ vulnerability detectors.

**Caption:**
GitHub CodeQL 2.25.3 is out. 🛡️ Swift 6.3 support lands. Five new default C/C++ security queries auto-scan for memory safety issues. Plus accuracy boosts across Python, Java, JS, C#. Your CI pipeline just got a sharper security eye. Is your code clean?

**Hashtags:**
#CodeQL #GitHub #SecurityTools #DevSecOps #StaticAnalysis #Swift #CPlusPlus #TechPulseDaily

---

## 💼 LinkedIn Post
GitHub released CodeQL 2.25.3 this week with an update set that security engineers will want to review carefully.

The highlights: Swift 6.3 language support brings automated vulnerability detection to the latest Swift release — critical for teams building iOS, macOS, and server-side Swift applications. Five new default C/C++ security queries targeting memory safety and injection patterns will now run automatically across all repositories using GitHub Advanced Security. Accuracy improvements land across Python, Java/Kotlin, JavaScript, C#, and GitHub Actions analysis.

The "default queries" designation is the important detail. These aren't optional rules your security team has to manually enable — they run automatically in CI for all Advanced Security users. That means millions of codebases will now be scanned for these vulnerability classes without any configuration changes.

For AppSec teams managing C/C++ codebases especially: review what the five new queries detect. Some findings may surface vulnerabilities that have been present in your codebase without detection.

Is your organization using CodeQL as part of your CI/CD security gates?

---

## 🐦 Twitter / X
1/ GitHub CodeQL 2.25.3 is out: Swift 6.3 support, five new default C/C++ security queries (auto-enabled for all Advanced Security users), plus accuracy improvements across Python, Java, JS, and C#. 🛡️

2/ The five new C/C++ queries run automatically — no configuration needed. If you're on Advanced Security with a C/C++ codebase, expect new findings this week. Review them carefully.

3/ Full release details: https://releasebot.io/updates/github

---

**Source:** [Releasebot / GitHub](https://releasebot.io/updates/github)
*TechPulse Daily · 2026-05-09 · Item 7/20*
