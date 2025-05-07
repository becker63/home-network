# 🏗️ HomeLab Infrastructure: GitOps + Immutable by Design

This project manages a fully declarative, GitOps-driven home lab infrastructure using Terraform, Talos, and Kubernetes. Everything is built around the idea that infrastructure should be immutable, recoverable, and reproducible anywhere — as long as similar hardware is available.

---

## 📦 Project Structure by Phase

### 📍 Phase 0: Bootstrap

Brings up minimal infrastructure to enable higher-level provisioning. This includes:

- **OCI VMs (x2)**
  - Provisioned using Terraform (Always Free tier)
  - No software is installed yet; treated as raw VM resources
  - Will host ingress services in Phase 1

- **Talos Machine Configs**
  - Static configs for the 3-node Kubernetes control plane (ThinkCentre mini PCs)
  - Applied using `talosctl`, wrapped with Python `invoke` scripts

- **Proxmox Host**
  - Bare-metal node to run dynamic workloads as VMs or LXCs
  - Initially bootstrapped manually or via future NetBoot automation

- **Initial Local Terraform State**
  - Used to bootstrap Ceph and the K8s cluster
  - Will be migrated to remote Ceph S3 once available

---

### 📍 Phase 1: Core Infrastructure

Installs foundational services across cloud and on-prem environments to support GitOps, remote access, and stateful workloads.

#### ☁️🌍 OCI Ingress Layer (OCI VMs + Public DNS)

Creates a highly available reverse proxy setup that exposes internal services to the internet.

- **FRP Server (`frps`)**
  - Runs on both OCI VMs
  - Accepts tunnels from internal `frpc` clients
  - Forwards traffic to internal services like Atlantis and Traefik

- **Keepalived**
  - Provides high availability via floating public IP
  - Ensures a single stable IP address across both OCI VMs

- **Public DNS**
  - Maps domain names (e.g., `gitops.example.com`) to the OCI floating IP
  - Enables stable, public access to the home network through FRP

#### 🏠 Home Kubernetes Cluster (Talos Nodes)

- **FRP Client (`frpc`)**
  - Runs as a static pod or DaemonSet
  - Maintains outbound tunnel to OCI `frps`
  - Forwards ingress traffic from the public internet into the cluster

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

## 📁 Repo Overview

```text
phases/
├── phase0-bootstrap/   # OCI VM provisioning, Talos machine configs
├── phase1-core/        # FRP (OCI/home), Ceph, PostgreSQL, Traefik, DNS
├── phase2-platform/    # Atlantis, cert management, GitHub runner
├── phase3-apps/        # Workloads: services, VMs, dashboards

scripts/                # Talosctl and SOPS automation (invoke tasks)
sops/                   # Encrypted secrets for use across phases
talosctl/               # Static machine configs for Talos cluster
