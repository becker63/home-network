import { Construct } from "constructs";
import { Chart } from "cdk8s";
import {
  Composition,
  CompositionSpecMode,
} from "../imports/apiextensions.crossplane.io";
import { Function as CrossplaneFunction } from "../imports/pkg.crossplane.io";
import {
  Resources,
  ResourcesResourcesPatchesType,
  ResourcesResourcesPatchesCombineStrategy,
} from "../imports/pt.fn.crossplane.io";

export class Nix_Server_CompositionChart extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // 1. Define build function
    new CrossplaneFunction(this, "FunctionBuildImage", {
      metadata: {
        name: "build-nixos-image",
      },
      spec: {
        package: "ghcr.io/your-org/builder:latest",
      },
    });

    // 2. Define patch-and-transform function
    new CrossplaneFunction(this, "FunctionPatchTransform", {
      metadata: {
        name: "function-patch-and-transform",
      },
      spec: {
        package:
          "xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.4.0",
      },
    });

    // 3. Define the Composition
    new Composition(this, "CompositionNixServer", {
      metadata: {
        name: "do-nixos-droplet",
      },
      spec: {
        compositeTypeRef: {
          apiVersion: "infra.example.org/v1alpha1",
          kind: "XNixServer",
        },
        mode: CompositionSpecMode.PIPELINE,
        pipeline: [
          {
            step: "build-nixos-image",
            functionRef: {
              name: "build-nixos-image",
            },
          },
          {
            step: "inject-droplet",
            functionRef: {
              name: "function-patch-and-transform",
            },
            input: Resources.manifest({
              resources: [
                {
                  name: "droplet",
                  base: {
                    apiVersion: "compute.digitalocean.crossplane.io/v1alpha1",
                    kind: "Droplet",
                    metadata: {
                      name: "nixos-droplet",
                    },
                    spec: {
                      forProvider: {
                        region: "placeholder", // to be patched
                        size: "s-1vcpu-1gb",
                        image: "placeholder", // patched from build function
                      },
                      providerConfigRef: { name: "default" },
                      writeConnectionSecretToRef: {
                        name: "nixos-droplet-secret",
                        namespace: "default",
                      },
                    },
                  },
                  patches: [
                    {
                      type: ResourcesResourcesPatchesType.COMBINE_FROM_COMPOSITE,
                      combine: {
                        strategy:
                          ResourcesResourcesPatchesCombineStrategy.STRING,
                        string: {
                          fmt: "%s|%s",
                        },
                        variables: [
                          { fromFieldPath: "context.imageSlug" }, // from build function
                          { fromFieldPath: "spec.region" }, // from XR
                        ],
                      },
                      toFieldPath: "spec.forProvider.image",
                    },
                    {
                      type: ResourcesResourcesPatchesType.FROM_COMPOSITE_FIELD_PATH,
                      fromFieldPath: "spec.region",
                      toFieldPath: "spec.forProvider.region",
                    },
                  ],
                },
              ],
            }),
          },
        ],
      },
    });
  }
}
