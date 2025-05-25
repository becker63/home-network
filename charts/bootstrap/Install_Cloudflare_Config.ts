import { Construct } from "constructs";
import { Chart } from "cdk8s";
import { Provider } from "../../imports/pkg.crossplane.io";
import {
  ProviderConfig,
  ProviderConfigSpecCredentialsSource,
} from "../../imports/cloudflare.upbound.io.ProviderConfig";

export class Bt_Install_Cloudflare extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Install the Cloudflare provider (local package)
    new Provider(this, "CloudflareProvider", {
      metadata: {
        name: "provider-cloudflare",
      },
      spec: {
        package: "provider-cloudflare",
        controllerConfigRef: {
          name: "default",
        },
      },
    });

    // Set up the ProviderConfig using ArgoCD-managed secrets
    new ProviderConfig(this, "CloudflareProviderConfig", {
      metadata: { name: "bt-cloudflare-providerconfig" },
      spec: {
        credentials: {
          source: ProviderConfigSpecCredentialsSource.SECRET,
          secretRef: {
            name: "argocd-secrets",
            namespace: "crossplane-system",
            key: "CLOUDFLARE_TOKEN_PROD",
          },
        },
      },
    });
  }
}
