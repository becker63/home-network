import schemas.go.frp_schema.frps as Server
import manifests
import helpers.emit_only_k8s as emiter

serverconfig = Server.ServerConfig {
    version: "v0.62.1"

    auth: Server.AuthServerConfig {
        token: "OVERWRITEME!"
    }

    bindAddr: "0.0.0.0"
    bindPort: 7000

    log: Server.LogConfig {
        level: "info"
        maxDays: 7
    }

    transport: Server.ServerTransportConfig {
        heartbeatTimeout: 60
    }

    detailedErrorsToClient: True
}

manifests.yaml_stream(
    emiter.emit_if_set({
        objs = [serverconfig]
    })
)