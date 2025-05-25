import { Construct } from "constructs";
import { Chart, Helm } from "cdk8s";

export class ntInstall_Argo_Crossplane extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Install Crossplane via Helm
    new Helm(this, "Crossplane", {
      chart: "crossplane",
      repo: "https://charts.crossplane.io/stable",
      releaseName: "crossplane",
      namespace: "crossplane-system",
      values: {
        args: ["--enable-composition-functions"],
      },
    });
  }
}
