import schemas.go.frp_schema.frpc as Client
import schemas.go.frp_schema.frpc.tcp_proxy as Tcp
import manifests

services = [
    # Expose Kubernetes ingress controller (port 80)
    Tcp.TcpproxyConfig {
        name: "k8s-ingress"
        $type: "tcp"
        localIP: "ingress-nginx-controller.kube-system.svc.cluster.local"
        localPort: 80
        remotePort: 30080
        loadBalancer: Tcp.LoadBalancerConfig {
            group: "k8s"
            groupKey: "OVERWRITEME!"
        }
        healthCheck: Tcp.HealthCheckConfig {
            $type: "http"
            path: "/"
            intervalSeconds: 10
            timeoutSeconds: 3
            maxFailed: 3
        }
    }
    # Expose Kubernetes control plane (port 6443)
    Tcp.TcpproxyConfig {
        name: "k8s-api"
        $type: "tcp"
        localIP: "kubernetes.default.svc.cluster.local"
        localPort: 6443
        remotePort: 30643
        loadBalancer: Tcp.LoadBalancerConfig {
            group: "k8s"
            groupKey: "OVERWRITEME!"
        }
        healthCheck: Tcp.HealthCheckConfig {
            $type: "tcp"
            intervalSeconds: 10
            timeoutSeconds: 3
            maxFailed: 3
        }
    }
]

clientconfig = Client.ClientConfig {
    version: "1.0.0"
    serverAddr: "frps.example.com"
    serverPort: 7000
    auth: Client.AuthClientConfig {
        token: "OVERWRITEME!"
    }
    proxies: services
}

manifests.yaml_stream([clientconfig])
