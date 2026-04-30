---
title: "CISA Flags Windows Zero-Click NTLM Hash Leak Left Behind by Incomplete February Patch"
date: 2026-04-30
category: security
category_label: "🔐 Security"
impact: "🔴 High"
source_url: https://www.theregister.com/2026/04/29/microsoft_zero_click_exploit/
source_name: "The Register"
item_number: 15
section: "🔐 Security & Infrastructure"
---

# 🔐 CISA Flags Windows Zero-Click NTLM Hash Leak Left Behind by Incomplete February Patch

> **🔐 Security** · 🔴 High · 2026-04-30

---

## 📋 Summary
CISA added CVE-2026-32202, a zero-click Windows NTLM hash leak vulnerability, to its Known Exploited Vulnerabilities (KEV) Catalog. The flaw is a remnant of an incomplete patch Microsoft issued in February 2026 for CVE-2026-21510, a remote code execution vulnerability. No user interaction is required to trigger the NTLM hash leak, which can allow attackers to perform relay attacks and potentially compromise Active Directory environments. Federal agencies must patch by May 12.

## 💡 Why It Matters
NTLM hash relay attacks are a classic but devastatingly effective attack pattern in Windows enterprise environments. Leaked NTLM credentials can be relayed to authenticate to other systems in the network without cracking the password. The zero-click nature means no phishing or social engineering is needed — just network access is sufficient to trigger credential theft.

## 🔍 What Is This?
NTLM (NT LAN Manager) is a legacy Windows authentication protocol still widely used in enterprise networks. An "NTLM hash" is an encoded form of a user's password. If an attacker can steal that hash, they can use it to authenticate as that user on other systems — a technique called "pass-the-hash." Zero-click means this can happen without the victim doing anything.

## 🔭 Looking Ahead
This vulnerability underscores the systemic risk of NTLM in modern Windows environments. Organizations should consider this a strong signal to accelerate NTLM deprecation and migration to Kerberos or modern authentication protocols, in addition to applying the patch.

---

## 📱 Instagram Slide

**Hook:**
Microsoft patched a bug in February. They missed something. Now it is being exploited.

**Caption:**
Microsoft patched a bug in February. They missed something. CVE-2026-32202 is what was left behind — a zero-click Windows flaw that leaks your credentials without you doing a thing. CISA says patch by May 12. Enterprise Windows admins: this one needs to go to the top of the queue.

**Hashtags:**
#Cybersecurity #Windows #NTLM #ZeroDay #InfoSec #CISA #TechNews #TechPulseDaily

---

## 💼 LinkedIn Post
CVE-2026-32202 is a textbook example of why "patch incomplete" scenarios are some of the most dangerous in enterprise security. In February 2026, Microsoft patched CVE-2026-21510, a remote code execution vulnerability in Windows. It turned out the patch was incomplete — CVE-2026-32202 is what remained. This residual flaw allows zero-click NTLM hash leakage: no user interaction, no phishing required. An attacker with network access can trigger credential theft silently. CISA has added it to the KEV catalog with a May 12 remediation deadline for federal agencies. The broader lesson here extends beyond this specific CVE: security teams should monitor for "incomplete patch" follow-on CVEs whenever Microsoft patches a high-severity remote code execution vulnerability. This pattern has appeared repeatedly in recent years. For organizations heavily reliant on NTLM in their Active Directory environments, this is also a signal to evaluate your NTLM deprecation roadmap. #Cybersecurity #Windows #NTLM #ZeroDay #CISA #ActiveDirectory #InfoSec

---

## 🐦 Twitter / X
1/ CISA added CVE-2026-32202 to its KEV catalog. It's a zero-click Windows NTLM hash leak — no user interaction needed. It's the remnant of an INCOMPLETE patch Microsoft shipped in February. 🔴 Patch by May 12.

2/ An attacker with network access can steal your Windows credentials without you clicking anything. Those credentials can then be relayed to compromise other systems. Classic NTLM relay risk, modern zero-click trigger.

3/ Security lesson: whenever Microsoft incompletely patches a high-severity RCE, watch for follow-on CVEs. They're becoming a pattern. Source: https://www.theregister.com/2026/04/29/microsoft_zero_click_exploit/

---

**Source:** [The Register](https://www.theregister.com/2026/04/29/microsoft_zero_click_exploit/)
*TechPulse Daily · 2026-04-30 · Item 15/20*
