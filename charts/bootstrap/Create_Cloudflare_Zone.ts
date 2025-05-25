import { Construct } from "constructs";
import { Chart } from "cdk8s";
import { Zone } from "../../imports/zone.cloudflare.upbound.io.Zone";

export class bt_Cloudflare_Zone extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new Zone(this, "BeckersLabZone", {
      metadata: {
        name: "beckers-lab-dev-zone",
      },
      spec: {
        forProvider: {
          zone: "beckers-lab.dev",
          type: "full", // Have cloudflare manage our domain entirely
          plan: "free",
        },
        providerConfigRef: {
          name: "default",
        },
      },
    });
  }
}
