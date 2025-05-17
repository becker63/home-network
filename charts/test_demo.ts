import { Chart, ChartProps, Size } from "cdk8s";
import { Construct } from "constructs";
import { Deployment, Service, ServiceType, Cpu } from "cdk8s-plus-32";

export class DemoTestChart extends Chart {
  constructor(scope: Construct, id: string, props?: ChartProps) {
    super(scope, id, props);

    const deployment = new Deployment(this, "nginx-deployment", {
      containers: [
        {
          name: "nginx",
          image: "nginx:1.25.3",
          port: 80,
          resources: {
            cpu: {
              request: Cpu.millis(100),
              limit: Cpu.millis(500),
            },
            memory: {
              request: Size.mebibytes(128),
              limit: Size.mebibytes(512),
            },
          },
        },
      ],
    });

    new Service(this, "nginx-service", {
      type: ServiceType.CLUSTER_IP,
      ports: [
        {
          port: 80,
          targetPort: 80,
        },
      ],
      selector: deployment,
    });
  }
}
