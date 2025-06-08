import schemas.go.frp_schema.frpc as Client
import schemas.go.frp_schema.frpc.tcp_proxy as Tcp
import manifests

# Named vars = dont export
config = Client.ClientConfig {
    version: "1.0.0"
    serverAddr: "frps.example.com"
    serverPort: 7000
    auth: Client.AuthClientConfig {
        token: "your-shared-token"
    }
    proxies: [
        Tcp.TcpproxyConfig {
            name: "headlamp"
            $type: "tcp"
            localIP: "headlamp.kube-system.svc.cluster.local"
            localPort: 80
            remotePort: 30080
            loadBalancer: Tcp.LoadBalancerConfig {
                group: "headlamp"
                groupKey: "your-shared-key"
            }
            healthCheck: Tcp.HealthCheckConfig {
                $type: "http"
                path: "/"
                intervalSeconds: 10
                timeoutSeconds: 3
                maxFailed: 3
            }
        }
    ]
}

manifests.yaml_stream(config)
