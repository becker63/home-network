import schemas.go.frp_schema.frps as Server
import manifests

serverconfig = Server.ServerConfig {
    version: "1.0.0"

    # Basic server listener config to match frpc
    bindAddr: "0.0.0.0"
    bindPort: 7000

    # Basic logging
    log: Server.LogConfig {
        level: "info"
        maxDays: 7
    }

    # Optional transport settings if needed (can be omitted for defaults)
    transport: Server.ServerTransportConfig {
        heartbeatTimeout: 60
    }

    # Optional features to simplify
    enablePrometheus: True
    detailedErrorsToClient: True
}

manifests.yaml_stream(serverconfig)
