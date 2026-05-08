---
title: "Kubernetes v1.36 Haru Released with 70 Enhancements Including Pod-Level Resource Managers"
date: 2026-05-08
category: devtools
category_label: "💻 Engineering & Dev Tools"
impact: "🟡 Medium"
source_url: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/
source_name: "Kubernetes Blog"
item_number: 5
section: "💻 Engineering & Dev Tools"
---

# 💻 Kubernetes v1.36 Haru Released with 70 Enhancements Including Pod-Level Resource Managers

> **💻 Engineering & Dev Tools** · 🟡 Medium · 2026-05-08

---

## 📋 Summary
The Kubernetes project released v1.36, codenamed "Haru" (Spring in Japanese), on April 22, 2026. The release includes 70 enhancements: 18 graduated to Stable, 25 entering Beta, and 25 reaching Alpha. Key features include Pod-Level Resource Managers (alpha) for performance-sensitive workloads, Declarative Validation for Kubernetes native types reaching General Availability, and SELinux volume mounting improvements that eliminate slow recursive relabeling on pod startup.

## 💡 Why It Matters
The Pod-Level Resource Managers feature addresses a long-standing pain point for ML training and HPC workloads that need fine-grained control over CPU, memory, and GPU assignment at the pod scope rather than the container scope. Meanwhile, the GA of Declarative Validation reduces configuration errors that have historically caused production incidents during cluster upgrades.

## 🔍 What Is This?
Kubernetes is the open-source system that most large cloud deployments use to run and manage containerized applications. Each new release adds features that make it easier to run demanding workloads reliably at scale — v1.36's focus is performance resource control and security policy enforcement.

## 🔭 Looking Ahead
Pod-level resource management in alpha today will likely GA by v1.38, at which point it becomes the recommended approach for AI/ML inference clusters — particularly important as GPU allocation becomes a primary cost control lever.

---

## 📱 Instagram Slide

**Hook:**
Kubernetes just shipped its biggest release of 2026 — 70 enhancements and counting.

**Caption:**
Kubernetes just shipped its biggest release of 2026 — 70 enhancements and counting. v1.36 "Haru" brings Pod-Level Resource Managers, Declarative Validation GA, and faster pod startup with smarter SELinux mounting. The cloud-native world keeps evolving. 👉 Follow TechPulse Daily for daily tech news.

**Hashtags:**
#Kubernetes #CloudNative #DevOps #K8s #Engineering #OpenSource #TechNews #TechPulseDaily

---

## 💼 LinkedIn Post
Kubernetes v1.36 "Haru" landed on April 22, 2026, and it's a dense release: 70 enhancements across alpha, beta, and stable milestones.

The most significant new capability is Pod-Level Resource Managers (alpha) — a more flexible resource management model that lets teams assign CPU, memory, and accelerators at the pod level rather than per-container. This is exactly what AI/ML inference and HPC workloads have needed for efficient GPU utilization.

Other highlights: Declarative Validation for Kubernetes native types is now GA, reducing the class of configuration errors that cause cluster upgrade failures. SELinux volume mounting improvements eliminate the slow recursive relabeling process that historically delayed pod startup on security-hardened clusters.

For platform engineering teams managing GPU-intensive workloads, v1.36 is worth scheduling upgrade testing soon. The alpha features in this release often reach GA within two minor versions.

What Kubernetes enhancement are you most eager to see stabilize?

## 🐦 Twitter / X
1/ Kubernetes v1.36 "Haru" is out! 70 enhancements: 18 stable, 25 beta, 25 alpha. The headline feature: Pod-Level Resource Managers (alpha) — finally, fine-grained CPU/GPU/memory control at the pod scope. 🧵

2/ Other wins: Declarative Validation for K8s native types hits GA (fewer config errors during upgrades), and SELinux volume mounting is improved — no more slow recursive relabeling slowing down pod startup.

3/ Full release notes + upgrade guide: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/

---

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
*TechPulse Daily · 2026-05-08 · Item 5/20*
