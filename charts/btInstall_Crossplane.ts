import { Construct } from "constructs";
import { Chart, Helm } from "cdk8s";
import { Provider } from "../imports/pkg.crossplane.io";

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

    // Install DigitalOcean provider via CRD
    new Provider(this, "ProviderDigitalOcean", {
      metadata: {
        name: "provider-digitalocean",
      },
      spec: {
        package:
          "xpkg.upbound.io/crossplane-contrib/provider-digitalocean:v0.2.0",
      },
    });
  }
}
