---
title: "Three Microsoft Defender Zero-Days Actively Exploited, Two Remain Unpatched"
date: 2026-04-29
category: security
category_label: "🔐 Security"
impact: "🔴 High"
source_url: "https://thehackernews.com/2026/04/three-microsoft-defender-zero-days.html"
source_name: "The Hacker News"
item_number: 14
section: "🔐 Security & Infrastructure"
---

# 🔐 Three Microsoft Defender Zero-Days Actively Exploited, Two Remain Unpatched

> **🔐 Security** · 🔴 High · 2026-04-29

---

## 📋 Summary
Three zero-day vulnerabilities in Microsoft Defender — named BlueHammer, RedSun, and UnDefend — are being actively exploited in the wild, with two of the three still unpatched as of publication. BlueHammer (CVE-2026-33825), disclosed publicly on April 7, enables local privilege escalation from an unprivileged user to SYSTEM level on fully patched Windows 10 and 11. Active weaponization of BlueHammer was observed beginning April 10, with RedSun and UnDefend PoC exploits following on April 16.

## 💡 Why It Matters
Microsoft Defender is the default antivirus and endpoint protection platform on over one billion Windows devices. A privilege escalation zero-day in Defender means attackers who gain any foothold on a system — via phishing, for example — can immediately escalate to full system control. With two of the three vulnerabilities still unpatched, the window of exposure remains open for a significant portion of the Windows ecosystem.

## 🔍 What Is This?
A privilege escalation vulnerability allows an attacker who has limited access to a computer (like a standard user account) to gain complete administrative control over the entire system. Combined with an initial access technique like phishing, this turns a low-severity intrusion into a complete system compromise.

## 🔭 Looking Ahead
Until patches are released for RedSun and UnDefend, organizations should implement compensating controls: restrict local access, monitor for suspicious SYSTEM-level process creation, and ensure endpoint detection tools are updated with behavioral signatures for known exploit patterns.

---

## 📱 Instagram Slide

**Hook:**
Three Defender zero-days. All being exploited right now. Two still don't have patches.

**Caption:**
BlueHammer, RedSun, UnDefend — three Windows Defender zero-days being actively exploited. One patched. Two still open. All three allow attackers to go from basic user to full system control on fully patched Windows. This is serious.

**Hashtags:**
#Cybersecurity #WindowsDefender #ZeroDay #BlueHammer #InfoSec #MicrosoftSecurity #TechNews #TechPulseDaily

---

## 💼 LinkedIn Post
Security teams need to be aware: three Microsoft Defender zero-day vulnerabilities — BlueHammer (CVE-2026-33825), RedSun, and UnDefend — are all under active exploitation, and two of the three remain unpatched.

BlueHammer enables local privilege escalation from standard user to SYSTEM level on fully patched Windows 10 and 11. It was publicly disclosed with a working PoC on April 7, weaponized by April 10. RedSun and UnDefend PoC exploits followed on April 16.

The security risk profile here is significant: Microsoft Defender is the default security layer on over a billion Windows devices. A Defender escalation zero-day means the very tool protecting systems can be leveraged against them.

Recommended compensating controls until patches are available: monitor for anomalous SYSTEM-level process creation, enforce least-privilege access rigorously, deploy behavioral detection rules for known BlueHammer exploit signatures, and restrict physical and RDP access to sensitive systems.

---

## 🐦 Twitter / X
1/ Three Microsoft Defender zero-days — BlueHammer, RedSun, UnDefend — are all being actively exploited. Two have no patch yet.

2/ BlueHammer enables privilege escalation from standard user to SYSTEM on fully patched Win 10/11. Weaponized since April 10. PoC for the other two dropped April 16.

3/ Defender on 1B+ Windows devices. Two unpatched. Compensating controls needed now. Source: https://thehackernews.com/2026/04/three-microsoft-defender-zero-days.html

---

**Source:** [The Hacker News](https://thehackernews.com/2026/04/three-microsoft-defender-zero-days.html)
*TechPulse Daily · 2026-04-29 · Item 14/20*
