import schemas.go.frp_schema.frps as Server

Server.ServerConfig {
    version: "1.0.0",

    bindAddr: "0.0.0.0",
    bindPort: 7000,
    proxyBindAddr: "0.0.0.0",
    quicBindPort: 7001,
    kcpBindPort: 7002,
    vhostHTTPPort: 8080,
    vhostHTTPSPort: 8443,
    vhostHTTPTimeout: 60,
    tcpmuxHTTPConnectPort: 8081,
    tcpmuxPassthrough: True,
    udpPacketSize: 1500,
    userConnTimeout: 10,

    allowPorts: [
        Server.PortsRange {
            start: 10000,
            end: 20000
        },
        Server.PortsRange {
            single: 8088
        }
    ],

    auth: Server.AuthServerConfig {
        method: "oidc",
        token: "server-token",
        additionalScopes: ["HeartBeats", "NewWorkConns"],
        oidc: Server.AuthOidcserverConfig {
            audience: "https://api.example.com",
            issuer: "https://auth.example.com",
            skipExpiryCheck: False,
            skipIssuerCheck: False
        }
    },

    log: Server.LogConfig {
        level: "debug",
        to: "/var/log/frps.log",
        maxDays: 7,
        disablePrintColor: False
    },

    transport: Server.ServerTransportConfig {
        heartbeatTimeout: 90,
        maxPoolCount: 10,
        tcpMux: True,
        tcpKeepalive: 60,
        tcpMuxKeepaliveInterval: 30,
        quic: Server.Quicoptions {
            maxIncomingStreams: 100,
            maxIdleTimeout: 120,
            keepalivePeriod: 20
        },
        tls: Server.TlsserverConfig {
            force: True,
            serverName: "example.com",
            certFile: "/etc/tls/server-cert.pem",
            keyFile: "/etc/tls/server-key.pem",
            trustedCaFile: "/etc/tls/ca.pem"
        }
    },

    sshTunnelGateway: Server.SshtunnelGateway {
        authorizedKeysFile: "/etc/frps/ssh/authorized_keys",
        bindPort: 2222,
        privateKeyFile: "/etc/frps/ssh/id_rsa",
        autoGenPrivateKeyPath: "/etc/frps/ssh/id_rsa.auto"
    },

    subDomainHost: "frps.example.com",
    enablePrometheus: True,
    detailedErrorsToClient: True,
    custom404Page: "/var/www/404.html",

    httpPlugins: [
        Server.HttppluginOptions {
            name: "authz",
            addr: "http://127.0.0.1:9000",
            path: "/plugin/authz",
            ops: ["NewProxy", "Ping"],
            tlsVerify: False
        }
    ],

    webServer: Server.WebServerConfig {
        addr: "127.0.0.1",
        port: 7500,
        user: "admin",
        password: "securepass",
        pprofEnable: True,
        assetsDir: "/var/www/assets",
        tls: Server.Tlsconfig {
            serverName: "example.com",
            certFile: "/etc/tls/web-cert.pem",
            keyFile: "/etc/tls/web-key.pem",
            trustedCaFile: "/etc/tls/ca.pem"
        }
    }
}