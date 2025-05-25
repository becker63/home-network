import { Construct } from "constructs";
import { Chart, Helm, ApiObject } from "cdk8s";
import * as fs from "fs";
import * as path from "path";

export class InstallGithubActionsRunner extends Chart {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const namespace = "actions-runner-system";

    // 1. Load the GitHub PAT from a local secrets file
    const secretsPath = path.join(process.cwd(), ".secrets.json");
    const secrets = JSON.parse(fs.readFileSync(secretsPath, "utf8"));
    const githubToken = secrets.github_token;

    if (!githubToken) {
      throw new Error('Missing "github_token" in .secrets.json');
    }

    // 2. Create the Kubernetes Secret
    new ApiObject(this, "GithubPATSecret", {
      apiVersion: "v1",
      kind: "Secret",
      metadata: {
        name: "controller-manager",
        namespace: namespace,
      },
      type: "Opaque",
      data: {
        // Kubernetes secrets must be base64-encoded
        github_token: Buffer.from(githubToken).toString("base64"),
      },
    });

    // 3. Install the ARC Controller
    new Helm(this, "ARCController", {
      chart: "gha-runner-scale-set-controller",
      releaseName: "arc-controller",
      repo: "oci://ghcr.io/actions/actions-runner-controller-charts",
      namespace,
    });

    // 4. Install the ARC Runner Set
    new Helm(this, "RunnerScaleSet", {
      chart: "gha-runner-scale-set",
      releaseName: "arc-runner-set",
      repo: "oci://ghcr.io/actions/actions-runner-controller-charts",
      namespace,
      values: {
        githubConfigUrl: "https://github.com/YOUR_ORG/YOUR_REPO",
        githubConfigSecret: {
          name: "controller-manager",
        },
        template: {
          spec: {
            containers: [
              {
                name: "runner",
                image: "ghcr.io/actions/runner:latest",
              },
            ],
          },
        },
      },
    });
  }
}
