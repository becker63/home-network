import { Construct } from "constructs";
import { Chart, Helm } from "cdk8s";

export class InstallExternalSecretsOperator extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new Helm(this, "ExternalSecretsOperator", {
      chart: "external-secrets",
      repo: "https://charts.external-secrets.io",
      releaseName: "external-secrets",
      namespace: "external-secrets",
      values: {
        installCRDs: true, // ensures CRDs are installed
      },
    });
  }
}
