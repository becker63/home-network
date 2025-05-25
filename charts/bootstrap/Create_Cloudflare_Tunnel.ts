import { Construct } from "constructs";
import { Chart } from "cdk8s";
import { TunnelRoute } from "../../imports/argo.cloudflare.upbound.io.TunnelRoute";

function createTunnelRoute(
  chart: Chart,
  name: string,
  network: string,
  comment: string,
) {
  return new TunnelRoute(chart, `TunnelRoute-${name}`, {
    metadata: { name },
    spec: {
      forProvider: {
        network,
        comment,
        tunnelIdRef: { name: "argocd-tunnel" },
      },
      providerConfigRef: { name: "default" },
    },
  });
}

export class Bt_Cloudflare_Argo_Tunnel_Route extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    createTunnelRoute(
      this,
      "argocd-tunnel-route-test",
      "argocd.internal.test",
      "Expose ArgoCD",
    );

    createTunnelRoute(
      this,
      "dashboard-tunnel-route-test",
      "dashboard.internal.test",
      "Expose internal dashboard",
    );
  }
}
