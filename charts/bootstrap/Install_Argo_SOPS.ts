import { Construct } from "constructs";
import { Chart, Helm } from "cdk8s";
import { Namespace } from "cdk8s-plus-32"; // or appropriate cdk8s-plus version

export class bt_Install_ArgoCD_AVP extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Create namespace for ArgoCD
    new Namespace(this, "ArgoCDNamespace", {
      metadata: {
        name: "argocd",
      },
    });

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
                  args: ["helm template . --values values.yaml"]
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
              ],
            },
          ],
          "plugin.volumes": [
            {
              name: "sops-key",
              secret: { secretName: "sops-age-key" },
            },
          ],
        },
      },
    });
  }
}
