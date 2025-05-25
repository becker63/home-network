import { Chart, ChartProps, ApiObject, JsonPatch, Size } from "cdk8s";
import { Construct } from "constructs";
import { Deployment, Service, ServiceType, Cpu } from "cdk8s-plus-32";

export class NginxChart extends Chart {
  constructor(
    scope: Construct,
    id: string = "nginx-chart",
    props?: ChartProps,
  ) {
    super(scope, id, props);

    const labels = { app: "nginx-demo" };

    const dep = new Deployment(this, "nginx-deployment", {
      metadata: { name: "nginx-deployment", labels },
      replicas: 1,
      containers: [
        {
          name: "nginx",
          image: "nginx:stable",
          port: 80,
          resources: {
            cpu: {
              request: Cpu.millis(100),
              limit: Cpu.millis(200),
            },
            memory: {
              request: Size.mebibytes(64),
              limit: Size.mebibytes(128),
            },
          },
        },
      ],
    });

    dep.podMetadata.addLabel("app", "nginx-demo");

    ApiObject.of(dep).addJsonPatch(
      JsonPatch.add("/spec/selector/matchLabels/app", "nginx-demo"),
      JsonPatch.add("/spec/template/metadata/labels/app", "nginx-demo"),
    );

    new Service(this, "nginx-service", {
      metadata: { name: "nginx-service" },
      type: ServiceType.CLUSTER_IP,
      ports: [{ port: 80, targetPort: 80 }],
      selector: dep,
    });
  }
}
