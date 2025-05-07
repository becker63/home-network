# 🏗️ HomeLab Infrastructure: GitOps + Immutable by Design

This project manages a fully declarative, GitOps-driven home lab infrastructure using Terraform, Talos, and Kubernetes. Everything is built around the idea that infrastructure should be immutable, recoverable, and reproducible anywhere — as long as similar hardware is available.

---

## 🧱 Hardware Overview

This project is designed to run on the following physical and cloud infrastructure:

### 🖥️ On-Prem Hardware

- **3× ThinkCentre Mini PCs**
  - Run Talos Linux
  - Form a high-availability Kubernetes control plane
  - Host critical stateful services (Ceph, Postgres, Atlantis, etc.)
  - Networked behind a home router
  - Intended to be resilient and fault-tolerant

- **1× Proxmox Bare-Metal Node**
  - Runs dynamic workloads as VMs or LXCs
  - Used for less critical, stateful, or experimental services
  - Terraform-managed (via Atlantis in Phase 3)

- **OpenWRT Router**

### ☁️ Cloud Resources

- **2× Oracle Cloud (OCI) Always Free VMs**
  - Publicly reachable, external ingress layer
  - Run `frps` and `keepalived` for reverse tunneling and failover
  - Used to expose internal services like Atlantis and Ceph

---

## 📦 Project Structure by Phase

### 📍 Phase 0: Bootstrap

Brings up the minimal infrastructure required to support later provisioning remotely. This includes:

- **OCI VMs (x2)**
  - Provisioned using Terraform (Always Free tier)
  - Hosts ingress services (FRP server + keepalived)
  - Public-facing tunnel endpoint for home cluster access

- **FRP Server (`frps`)**
  - Installed on both OCI VMs
  - Accepts tunnels from internal `frpc` clients in the home cluster
  - Enables external access to Ceph (S3) for remote Terraform state

- **Keepalived**
  - Provides a floating public IP across the OCI VMs
  - Ensures high-availability access to the `frps` service

- **Public DNS**
  - Points your domain (e.g., `gitops.example.com`) to the OCI floating IP
  - Enables external access to services tunneled through FRP

- **Talos Machine Configs**
  - Static configs for the 3-node Kubernetes control plane (ThinkCentre mini PCs)
  - Applied using `talosctl`, wrapped with Python `invoke` scripts

- **Proxmox Host**
  - Bare-metal node to run dynamic workloads as VMs or LXCs
  - Initially bootstrapped manually or via future NetBoot automation

- **Initial Local Terraform State**
  - Used to provision OCI VMs and Talos configs
  - Will later migrate to Ceph (S3) once that backend is stood up in Phase 1

---

### 📍 Phase 1: Core Infrastructure

Installs foundational services inside the Kubernetes cluster to support GitOps, persistent infrastructure, and cluster ingress.

#### 🏠 Home Kubernetes Cluster (Talos Nodes)

- **FRP Client (`frpc`)**
  - Runs as a static pod or DaemonSet
  - Maintains an outbound tunnel to OCI `frps`
  - Forwards ingress traffic from the internet into the cluster

- **Ceph (S3 Gateway Mode)**
  - MinIO-compatible object storage deployed across the Talos control plane
  - Stores:
    - Remote Terraform state
    - Optional object storage (e.g., backups, logs)

- **PostgreSQL**
  - Stores lock metadata for Terraform state (used by Atlantis)
  - Runs as a singleton or HA StatefulSet

- **Traefik**
  - Ingress controller for the cluster
  - Provides HTTPS via Let’s Encrypt (ACME DNS-01 challenge)
  - Exposes services like Atlantis and Ceph UIs to the internet through FRP

---

### 📍 Phase 2: Platform Layer

Deploys the automation tools that manage infrastructure changes through GitOps.

- **Atlantis**
  - Automates Terraform via GitHub pull requests
  - Runs inside the Kubernetes cluster
  - Uses:
    - Ceph S3 for tfstate
    - PostgreSQL for state locking

- **GitHub Runner (optional)**
  - Runs inside the cluster to support CI/CD pipelines
  - Useful for running workflows that affect infrastructure

- **Cert Management**
  - Handled by Traefik using ACME + DNS challenge
  - Issues and auto-renews TLS certificates for public services

---

### 📍 Phase 3: Applications

Defines all homelab services and workloads.

- **Home Services**
  - Media servers, observability tools, self-hosted dashboards, etc.
  - Deployed declaratively via Terraform or Helm

- **Proxmox VMs / LXCs**
  - Managed using Terraform
  - Used for workloads that don’t belong in Kubernetes or require special isolation

---

## 🔐 Secrets Management

- **SOPS + age**
  - Used for encrypting:
    - Talos machine and cluster secrets
    - Terraform credentials
    - Atlantis secrets
  - Secrets are decrypted at runtime using automation (via `invoke` or Justfile)

---

## 🔁 DevOps Workflow

1. Developer pushes Terraform or Helm config to GitHub
2. Atlantis triggers `terraform plan`
3. On PR approval, Atlantis runs `terraform apply`
4. Terraform state is stored in Ceph S3; lock state in PostgreSQL
5. Services are deployed and managed declaratively via Kubernetes

---

