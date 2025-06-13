import schemas.go.frp_schema.frps as Server
import manifests



serverconfig = Server.ServerConfig {
    version: "v0.62.1"

    # Server-side token must match client `auth.token`
    auth: Server.AuthServerConfig {
        token: "OVERWRITEME!"
    }

    # Basic listener config
    bindAddr: "0.0.0.0"
    bindPort: 7000

    # Logging
    log: Server.LogConfig {
        level: "info"
        maxDays: 7
    }

    # Transport (optional)
    transport: Server.ServerTransportConfig {
        heartbeatTimeout: 60
    }

    # Enable optional features
    detailedErrorsToClient: True
}

manifests.yaml_stream([serverconfig])
