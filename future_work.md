## 📦 Chart Composition Order

This is the order in which each CDK8s chart should be instantiated to ensure dependencies are correctly resolved:

1. **ArgoCDCore** – Sets up the `argocd` namespace and minimal ArgoCD deployment.
2. **CrossplaneCore** – Sets up the `crossplane-system` namespace.
3. **DOProvider** – Configures the DigitalOcean provider for Crossplane.
4. **ArgoWorkflowBuilder** – (Optional for testing, nixos build tests will be performed elseware) Defines the Argo Workflow to build, upload, and register the NixOS image.
5. **NixOSImageSecret** – (Optional for testing) writes the image slug into a `Secret`.
6. **ImageReader** – Uses `provider-kubernetes` to extract the image slug from the Secret and write a connection secret.
7. **FinalDroplet** – Provisions the DigitalOcean Droplet using the image slug from the connection secret.

This order ensures that foundational services (ArgoCD, Crossplane) are ready before applying higher-level resources (like VMs).

# Chart Order in Kubernetes

## ✅ Does chart order matter?

Take a look at the bootstrap code below
```typescript
await execa('kubectl', ['apply', '-f', SYNTH_OUTPUT])
```

This applies **all manifests at once** without explicit ordering.

## Key Points

* **Technical reality**: Kubernetes handles ordering internally
  * Creates namespaces before namespaced resources
  * Registers CRDs before CRs
  * Controllers reconcile when available
  * Eventually consistent and controller-driven

* **Best practice**: Still organize conceptually
  1. Foundational resources first (Namespaces, CRDs)
  2. Controllers next (ArgoCD, Crossplane)
  3. Configuration (Secrets, ProviderConfigs)
  4. Application logic
  5. Final infrastructure

* **Benefits**: Improves clarity, testing, debugging, and maintainability

## ✅ TL;DR
Kubernetes resolves dependencies automatically, but conceptual ordering improves code quality and maintainability.

### Why not hardcode the image slug?

Hardcoding works for simple cases, but in serious GitOps setups, dynamic slugs are preferred because:

- **Immutable builds**: Each build should produce a unique, traceable image slug (e.g. `nixos-20240518`), not overwrite `nixos-latest`.
- **Automatic updates**: Argo can write the new slug to a Secret; Crossplane watches and reacts — no manual edits needed.
- **Separation of concerns**: Build systems produce artifacts; infra systems consume them — the Secret bridges them.
- **Promotion workflows**: You can test/promote builds across environments via secrets without touching infra code.

Using secrets ensures clean, dynamic, and fully declarative infra.

# The bootstrap code

## 🧰 `scripts/bootstrap.ts`

```ts
import path from 'path';
import fs from 'fs';
import { execa } from 'execa';

const SYNTH_OUTPUT = path.join(__dirname, '..', 'dist', 'sut.k8s.yaml');

async function main() {
  console.log('🛠 Synthesizing CDK8s bootstrap chart...');
  await execa('npx', ['cdk8s', 'synth'], { stdio: 'inherit' });

  if (!fs.existsSync(SYNTH_OUTPUT)) {
    console.error(`❌ Could not find synthesized output at ${SYNTH_OUTPUT}`);
    process.exit(1);
  }

  console.log('🚀 Applying bootstrap manifest...');
  await execa('kubectl', ['apply', '-f', SYNTH_OUTPUT], { stdio: 'inherit' });

  // Optional: Wait for ArgoCD to be ready
  console.log('⏳ Waiting for ArgoCD server deployment to become ready...');
  await execa('kubectl', [
    'wait',
    '--namespace', 'argocd',
    '--for=condition=available',
    '--timeout=120s',
    'deployment/argocd-server'
  ]);

  console.log('✅ Bootstrap complete.');
}

main().catch((err) => {
  console.error('❌ Bootstrap failed:', err);
  process.exit(1);
});
````

# The charts to write

## ArgoCD Core Chart

```typescript
// charts/sut/argocd.ts
import { Chart } from 'cdk8s';
import { Construct } from 'constructs';
import * as k8s from '../imports/k8s';

export class ArgoCDCore extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new k8s.KubeManifest(this, 'Namespace', {
      manifest: {
        apiVersion: 'v1',
        kind: 'Namespace',
        metadata: { name: 'argocd' }
      }
    });

    new k8s.KubeManifest(this, 'ServerDeployment', {
      manifest: {
        apiVersion: 'apps/v1',
        kind: 'Deployment',
        metadata: { name: 'argocd-server', namespace: 'argocd' },
        spec: {
          replicas: 1,
          selector: { matchLabels: { app: 'argocd-server' } },
          template: {
            metadata: { labels: { app: 'argocd-server' } },
            spec: {
              containers: [
                {
                  name: 'argocd-server',
                  image: 'quay.io/argoproj/argocd:v2.11.0',
                  ports: [{ containerPort: 8080 }]
                }
              ]
            }
          }
        }
      }
    });
  }
}
```

## Crossplane Core Chart

```typescript
// charts/sut/crossplane.ts
import { Chart } from 'cdk8s';
import { Construct } from 'constructs';
import * as k8s from '../imports/k8s';

export class CrossplaneCore extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new k8s.KubeManifest(this, 'CrossplaneNamespace', {
      manifest: {
        apiVersion: 'v1',
        kind: 'Namespace',
        metadata: { name: 'crossplane-system' }
      }
    });
  }
}
```

## DigitalOcean Provider Chart

```typescript
// charts/sut/provider.ts
import { Chart } from 'cdk8s';
import { Construct } from 'constructs';
import * as k8s from '../imports/k8s';

export class DOProvider extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new k8s.KubeManifest(this, 'ProviderConfigDO', {
      manifest: {
        apiVersion: 'digitalocean.crossplane.io/v1beta1',
        kind: 'ProviderConfig',
        metadata: { name: 'default' },
        spec: {
          credentials: {
            source: 'Secret',
            secretRef: {
              namespace: 'crossplane-system',
              name: 'do-creds',
              key: 'token'
            }
          }
        }
      }
    });
  }
}
```

## Argo Workflow Image Builder Chart

```typescript
// charts/sut/imagebuilder.ts
import { Chart } from 'cdk8s';
import { Construct } from 'constructs';
import * as k8s from '../imports/k8s';

export class ArgoWorkflowBuilder extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new k8s.KubeManifest(this, 'ImageBuildWorkflow', {
      manifest: {
        apiVersion: 'argoproj.io/v1alpha1',
        kind: 'Workflow',
        metadata: { name: 'nixos-image-builder' },
        spec: {
          entrypoint: 'build-upload-register',
          templates: [
            {
              name: 'build-upload-register',
              dag: {
                tasks: [
                  { name: 'build', template: 'build' },
                  { name: 'upload', dependencies: ['build'], template: 'upload' },
                  { name: 'register', dependencies: ['upload'], template: 'register' },
                  { name: 'write-secret', dependencies: ['register'], template: 'write-secret' }
                ]
              }
            },
            {
              name: 'build',
              container: {
                image: 'nixos/nix',
                command: ['sh', '-c'],
                args: ['nix build .#nixosConfigurations.vm.config.system.build.qcow2']
              }
            },
            {
              name: 'upload',
              container: {
                image: 'amazon/aws-cli',
                command: ['sh', '-c'],
                args: ['aws s3 cp ./result.qcow2 s3://your-bucket/nixos.qcow2']
              }
            },
            {
              name: 'register',
              container: {
                image: 'digitalocean/doctl',
                env: [
                  {
                    name: 'DIGITALOCEAN_ACCESS_TOKEN',
                    valueFrom: {
                      secretKeyRef: {
                        name: 'do-creds',
                        key: 'token'
                      }
                    }
                  }
                ],
                command: ['sh', '-c'],
                args: ['doctl compute image create nixos.qcow2 --image-url=https://your-bucket/nixos.qcow2 --region=nyc3 --name=nixos-latest']
              }
            },
            {
              name: 'write-secret',
              container: {
                image: 'bitnami/kubectl',
                command: ['sh', '-c'],
                args: ['kubectl create secret generic nixos-image --from-literal=image=nixos-latest --dry-run=client -o yaml | kubectl apply -f -']
              }
            }
          ]
        }
      }
    });
  }
}
```

## NixOS Write Image Secret Chart

```typescript
// charts/sut/writeimagesecret.ts
import { Chart } from 'cdk8s';
import { Construct } from 'constructs';
import * as k8s from '../imports/k8s';

export class NixOSImageSecret extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new k8s.KubeManifest(this, 'ImageSecret', {
      manifest: {
        apiVersion: 'v1',
        kind: 'Secret',
        metadata: {
          name: 'nixos-image',
          namespace: 'default'
        },
        stringData: {
          image: 'nixos-latest'
        }
      }
    });
  }
}
```

## Image Reader Chart

```typescript
// charts/sut/readsecret.ts
import { Chart } from 'cdk8s';
import { Construct } from 'constructs';
import * as k8s from '../imports/k8s';

export class ImageReader extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new k8s.KubeManifest(this, 'ReadImageSecret', {
      manifest: {
        apiVersion: 'kubernetes.crossplane.io/v1alpha1',
        kind: 'Object',
        metadata: { name: 'pull-nixos-image' },
        spec: {
          forProvider: {
            manifest: {
              apiVersion: 'v1',
              kind: 'Secret',
              metadata: { name: 'nixos-image', namespace: 'default' }
            }
          },
          connectionDetails: [{ name: 'image', fromFieldPath: 'data.image' }],
          writeConnectionSecretToRef: {
            name: 'nixos-connection',
            namespace: 'default'
          }
        }
      }
    });
  }
}
```

## Final Droplet Chart

```typescript
// charts/sut/droplet.ts
import { Chart } from 'cdk8s';
import { Construct } from 'constructs';
import * as k8s from '../imports/k8s';

export class FinalDroplet extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new k8s.KubeManifest(this, 'DigitalOceanDroplet', {
      manifest: {
        apiVersion: 'droplet.digitalocean.crossplane.io/v1alpha1',
        kind: 'Droplet',
        metadata: { name: 'reverse-proxy-droplet' },
        spec: {
          forProvider: {
            region: 'nyc3',
            image: '',  // Will be resolved from nixos-connection secret
            size: 's-1vcpu-1gb'
          },
          providerConfigRef: { name: 'default' },
          writeConnectionSecretToRef: {
            name: 'nixos-droplet-secret',
            namespace: 'default'
          }
        }
      }
    });
  }
}
```

## Main Application Entry Point

```typescript
// charts/sut/index.ts
import { App } from 'cdk8s';
import { ArgoCDCore } from './argocd';
import { CrossplaneCore } from './crossplane';
import { DOProvider } from './provider';
import { ArgoWorkflowBuilder } from './imagebuilder';
import { NixOSImageSecret } from './writeimagesecret';
import { ImageReader } from './readsecret';
import { FinalDroplet } from './droplet';

const app = new App();

new ArgoCDCore(app, 'argocd');
new CrossplaneCore(app, 'crossplane');
new DOProvider(app, 'provider');
new ArgoWorkflowBuilder(app, 'workflow');
new NixOSImageSecret(app, 'image-secret');
new ImageReader(app, 'image-reader');
new FinalDroplet(app, 'droplet');

app.synth();
```
