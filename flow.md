# 🔁 Full GitOps Infra Flow with Argo + Crossplane

This describes how your system boots, builds, provisions, and recovers from VM failures.

---

## ✅ Initial Bootstrap Flow

1. **Bootstrap runs**
   - `cdk8s synth` generates all charts
   - `kubectl apply -f` applies them all

2. **What gets deployed**
   - `ArgoCDCore`: minimal ArgoCD install
   - `CrossplaneCore`: Crossplane namespace
   - `DOProvider`: DigitalOcean provider config
   - `ArgoWorkflowBuilder`: defines reusable Argo Workflow template
   - `ArgoWorkflowTrigger`: Crossplane object that submits a *run* of the Workflow using `generateName`
   - `ImageReader`: pulls image slug from Secret → writes connection secret
   - `FinalDroplet`: provisions DigitalOcean VM using the image from the connection secret

3. **What happens at runtime**
   - Argo **executes the Workflow**
     - Builds the NixOS image
     - Uploads it
     - Registers it with DigitalOcean
     - Writes a `Secret` named `nixos-image` with the image slug (e.g., `nixos-latest`)
   - Crossplane:
     - Reads the `nixos-image` secret via `provider-kubernetes`
     - Writes a `nixos-connection` secret
     - Uses the slug from that to provision the VM

---

## 💥 What Happens if the VM Fails?

If the Droplet is deleted or fails out-of-band:

1. Crossplane sees the Droplet resource still exists in the cluster
2. It attempts to **recreate the Droplet**
3. It uses the same value from the existing `nixos-connection` secret
4. ✅ Recovery works — as long as the image is still valid

---

## 🧨 What if the image needs to be rebuilt?

Crossplane will not automatically re-run the Argo Workflow unless triggered.

To do that:

### ✅ You **delete the `nixos-image` Secret**

Then:

1. Crossplane's `ImageReader` fails to find the secret
2. Crossplane **re-reconciles** the `ArgoWorkflowTrigger` object
3. Because it's defined with `generateName:` and `deletionPolicy: Delete`
4. Crossplane creates a **new Argo Workflow run**
5. Argo builds and uploads a fresh image
6. A new `nixos-image` secret is written
7. Crossplane pulls the new slug → updates the `nixos-connection` secret
8. Droplet is recreated using the rebuilt image

---

## 🧠 Why This Works

- The image build is **declaratively triggered** by the presence/absence of a `Secret`
- Crossplane treats the `Object` as a controller-managed resource
- Argo runs workflows using `generateName:` so every run is fresh
- Everything is reconciled through Kubernetes — fully GitOps-compatible

---

## 🧰 Optional Enhancements

- Add a **CronJob** or controller to delete the secret on a schedule
- Add retry/backoff logic to your Argo Workflow steps
- Switch from `nixos-latest` to versioned slugs (e.g., `nixos-20240520`) for immutability

---

## ✅ TL;DR Flow Summary

| Event | What Happens |
|-------|--------------|
| Bootstrap | Argo Workflow runs → image built → Droplet provisioned |
| Droplet deleted | Crossplane recreates it using same image |
| Secret deleted | Crossplane re-runs Workflow → new image built |
