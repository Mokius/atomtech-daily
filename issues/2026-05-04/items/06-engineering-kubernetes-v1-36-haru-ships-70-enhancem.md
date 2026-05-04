---
title: "Kubernetes v1.36 Haru Ships 70 Enhancements Including User Namespaces GA"
date: 2026-05-04
category: engineering
category_label: "💻 Engineering"
impact: "🟡 Medium"
source_url: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/
source_name: "Kubernetes Blog"
item_number: 6
section: "💻 Engineering & Dev Tools"
---

# 💻 Kubernetes v1.36 Haru Ships 70 Enhancements Including User Namespaces GA

> **💻 Engineering** · 🟡 Medium · 2026-05-04

---

## 📋 Summary
Kubernetes v1.36, codenamed "Haru" (Spring in Japanese), was released April 22, 2026, delivering 70 enhancements: 18 graduating to Stable, 25 entering Beta, and 25 as new Alpha features. Key stable promotions include User Namespaces (GA for improved container security isolation), Mutating Admission Policies via CEL expressions (eliminating webhook overhead), Fine-grained Kubelet API Authorization, and SELinux Volume Mounting improvements. Notable alpha features include HPAScaleToZero enabled by default and ephemeral tokens for image pulls.

## 💡 Why It Matters
User Namespaces GA is a significant security milestone — it allows containers to run as "root" inside a container while mapping to an unprivileged user on the host, dramatically reducing attack surface for containerized workloads. The deprecation of Ingress NGINX (retired March 24, 2026) affects thousands of production clusters and requires migration planning. CEL-based Mutating Admission Policies reduce operational complexity for platform teams by eliminating external webhook infrastructure.

## 🔍 What Is This?
Kubernetes is the industry-standard system for managing containerized applications at scale — used by virtually every major cloud provider and enterprise running modern software. Think of it as the orchestration layer that decides where your apps run, how they scale, and how they recover from failures. Version 1.36 brings security improvements, better resource management, and reduced operational overhead for the teams managing these systems.

## 🔭 Looking Ahead
The HPA Scale to Zero feature — enabling Kubernetes to reduce workload replicas to zero during idle periods — will unlock significant cost savings for organizations running AI inference endpoints and batch processing jobs. Combined with improved resource managers, v1.36 sets the stage for more efficient AI workload scheduling in the 1.37 cycle.

---

## 📱 Instagram Slide

**Hook:**
Kubernetes v1.36 is out — and it's one of the most security-focused releases in years.

**Caption:**
Kubernetes Haru shipped 70 enhancements. User Namespaces is now GA. Ingress NGINX is retired. CEL-based policies replace webhooks. HPA can now scale to zero. Infrastructure just got safer and cheaper.

**Hashtags:**
#Kubernetes #CloudNative #DevOps #K8s #CloudComputing #CNCF #Engineering #TechPulseDaily

---

## 💼 LinkedIn Post
Kubernetes v1.36 "Haru" shipped April 22 with 70 enhancements, and a few deserve particular attention from platform and infrastructure teams.

User Namespaces is now Generally Available — a meaningful security win that lets containers run as root internally while mapping to unprivileged host users. This reduces the blast radius of container escapes significantly.

CEL-based Mutating Admission Policies graduate to Stable, replacing external webhook infrastructure with declarative, in-process validation. For platform teams running large multi-tenant clusters, this reduces operational overhead and eliminates a class of webhook availability issues.

Action item for ops teams: Ingress NGINX was officially retired on March 24, 2026. No further security patches will be issued. Migration planning should be a priority for any cluster relying on it.

Also worth watching: HPAScaleToZero entering Alpha means significant cost optimization opportunities for event-driven and AI inference workloads in the not-too-distant future.

Is your team already on a migration path away from Ingress NGINX?

---

## 🐦 Twitter / X
1/ Kubernetes v1.36 "Haru" is out. 70 enhancements: 18 stable, 25 beta, 25 alpha. The big security win: User Namespaces is now GA. Containers can safely "run as root" without host root privileges. Huge for container security.

2/ Also graduated to stable: CEL-based Mutating Admission Policies (bye webhooks), Fine-grained Kubelet Authorization, SELinux Volume Mounting. HPA Scale to Zero enters alpha. Big release for platform teams.

3/ Critical alert: Ingress NGINX was retired March 24. No more security patches. Migrate now. Full release notes: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/

---

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
*TechPulse Daily · 2026-05-04 · Item 6/20*
