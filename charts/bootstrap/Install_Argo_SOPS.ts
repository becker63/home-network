import { Construct } from "constructs";
import { Chart, Helm } from "cdk8s";
import { Namespace, Secret } from "cdk8s-plus-32";
import * as fs from "fs";
import * as path from "path";

export class bt_Install_ArgoCD_AVP extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Create namespace for ArgoCD
    new Namespace(this, "ArgoCDNamespace", {
      metadata: {
        name: "argocd",
      },
    });

    // Load secrets from secrets.json
    const secretsPath = path.join(process.cwd(), "secrets.json");
    if (!fs.existsSync(secretsPath)) {
      throw new Error(`❌ secrets.json not found at ${secretsPath}`);
    }
    const secretData = JSON.parse(fs.readFileSync(secretsPath, "utf8"));

    // Create project-secrets Secret in crossplane-system
    new Secret(this, "ProjectSecrets", {
      metadata: {
        name: "project-secrets",
        namespace: "crossplane-system",
      },
      stringData: secretData,
    });

    // Install ArgoCD with AVP sidecar configured
    new Helm(this, "ArgoCD", {
      chart: "argo-cd",
      repo: "https://argoproj.github.io/argo-helm",
      releaseName: "argo-cd",
      namespace: "argocd",
      values: {
        configs: {
          cm: {
            configManagementPlugins: `
              - name: avp
                init:
                  command: ["/bin/bash", "-c"]
                  args: ["cp /secrets/secrets.json ./secrets.json"]
                generate:
                  command: ["argocd-vault-plugin"]
                  args: ["generate", "./"]
            `,
          },
          "plugin.enabled": true,
          "plugin.sidecarContainers": [
            {
              name: "avp",
              image: "ghcr.io/argoproj-labs/argocd-vault-plugin:v1.16.0",
              command: ["/bin/argocd-vault-plugin"],
              args: ["server"],
              env: [
                { name: "AVP_TYPE", value: "sops" },
                { name: "SOPS_AGE_KEY_FILE", value: "/sops/keys.txt" },
              ],
              volumeMounts: [
                { name: "sops-key", mountPath: "/sops", readOnly: true },
                {
                  name: "project-secrets",
                  mountPath: "/secrets",
                  readOnly: true,
                },
              ],
            },
          ],
          "plugin.volumes": [
            { name: "sops-key", secret: { secretName: "sops-age-key" } },
            {
              name: "project-secrets",
              secret: {
                secretName: "project-secrets",
                optional: false,
              },
            },
          ],
        },
      },
    });
  }
}
