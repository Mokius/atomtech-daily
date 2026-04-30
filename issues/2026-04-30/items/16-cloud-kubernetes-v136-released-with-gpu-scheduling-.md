---
title: "Kubernetes v1.36 Released with GPU Scheduling Improvements and Fine-Grained Auth at GA"
date: 2026-04-30
category: cloud
category_label: "☁️ Cloud"
impact: "🟡 Medium"
source_url: https://kubernetes.io/blog/2026/03/30/kubernetes-v1-36-sneak-peek/
source_name: "Kubernetes.io"
item_number: 16
section: "🔐 Security & Infrastructure"
---

# ☁️ Kubernetes v1.36 Released with GPU Scheduling Improvements and Fine-Grained Auth at GA

> **☁️ Cloud** · 🟡 Medium · 2026-04-30

---

## 📋 Summary
Kubernetes v1.36 was released in late April 2026, bringing significant improvements to GPU and AI accelerator scheduling via enhanced Dynamic Resource Allocation (DRA), and graduating fine-grained kubelet API authorization to General Availability (GA). The release enables partial device allocation — letting multiple workloads share a GPU without full reservation — and includes dozens of additional enhancements and deprecations focused on AI workload efficiency and security.

## 💡 Why It Matters
As AI workloads increasingly run on Kubernetes clusters, the platform's ability to efficiently schedule and share GPU resources becomes critical to cost and performance. The DRA improvements directly address the "all or nothing" problem with GPU allocation that has plagued multi-tenant AI infrastructure. Kubelet auth at GA improves the security posture of every Kubernetes cluster.

## 🔍 What Is This?
Kubernetes is the industry-standard platform for running containerized software at scale. GPUs are specialized chips used for AI model training and inference. Previously, Kubernetes would reserve an entire GPU for a single workload even if it only needed a fraction. v1.36's DRA improvements allow fine-grained sharing, making GPU utilization far more efficient.

## 🔭 Looking Ahead
GPU sharing improvements in Kubernetes will reduce infrastructure costs for organizations running AI workloads at scale. Combined with Google's GKE Inference Gateway announced at Cloud Next, v1.36 positions Kubernetes as the definitive platform for production AI infrastructure.

---

## 📱 Instagram Slide

**Hook:**
Running AI on Kubernetes just got significantly more efficient.

**Caption:**
Running AI on Kubernetes just got significantly more efficient. v1.36 drops improved GPU scheduling — allocate only what you need, share the rest. Plus enhanced security with kubelet auth now GA. If you run AI workloads on K8s clusters, this release is worth your attention.

**Hashtags:**
#Kubernetes #CloudNative #DevOps #CNCF #GPU #AI #CloudInfrastructure #TechPulseDaily

---

## 💼 LinkedIn Post
Kubernetes v1.36 landed at the end of April with a release that matters particularly for organizations running AI workloads on Kubernetes infrastructure. The headline improvement is in Dynamic Resource Allocation (DRA): platform teams can now allocate fractional portions of a GPU or AI accelerator to individual workloads, rather than reserving the entire device. This addresses one of the most persistent inefficiencies in multi-tenant AI infrastructure — the "all-or-nothing" GPU reservation model that has historically left significant compute capacity idle. For a single large language model inference workload running at 30% GPU utilization, the remaining 70% was simply wasted. v1.36 changes that. The graduation of fine-grained kubelet API authorization to GA is also meaningful for enterprise security teams — it's a direct improvement to the attack surface of every Kubernetes cluster. For teams running AI inference on Kubernetes at scale, the GPU sharing improvements alone could meaningfully reduce infrastructure costs. #Kubernetes #CNCF #AI #CloudNative #DevOps #GPUComputing #PlatformEngineering

---

## 🐦 Twitter / X
1/ Kubernetes v1.36 is out. Key for AI workloads: DRA improvements that let you allocate just a fraction of a GPU to each workload, not the whole thing. Multi-tenant GPU sharing, finally done right. 🟡 Cost savings unlock.

2/ Also in v1.36: fine-grained kubelet API authorization graduates to GA. Every K8s cluster gets a better default security posture. Small headline, big security win.

3/ Combined with Google GKE Inference Gateway, Kubernetes is cementing its position as the platform for production AI infrastructure in 2026. Source: https://kubernetes.io/blog/2026/03/30/kubernetes-v1-36-sneak-peek/

---

**Source:** [Kubernetes.io](https://kubernetes.io/blog/2026/03/30/kubernetes-v1-36-sneak-peek/)
*TechPulse Daily · 2026-04-30 · Item 16/20*
