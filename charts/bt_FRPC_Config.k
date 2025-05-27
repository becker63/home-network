import frp_schema.frpc as Client

client_config: Client.ClientConfig {
    version: "1.0.0",  # required field
    serverAddr: "127.0.0.1",
    serverPort: 7000,
    log: Client.LogConfig {
        level: "info",
        to: "/var/log/frpc.log",
        maxDays: 7,
    },
    auth: Client.AuthClientConfig {
        method: "token",
        oidc: Client.AuthOidcclientConfig {
            clientID: "my-client-id",
            clientSecret: "my-client-secret",
            audience: "https://api.example.com",
            tokenEndpointURL: "https://auth.example.com/token",
            scope: "openid profile",
            additionalEndpointParams: {
                "param1": "value1",
                "param2": "value2",
            },
        },
    },
    transport: Client.ClientTransportConfig {
        protocol: "tcp",
        tls: Client.TlsclientConfig {
            enable: True,
            serverName: "example.com",
            trustedCaFile: "/etc/tls/ca.pem",
            certFile: "/etc/tls/client-cert.pem",
            keyFile: "/etc/tls/client-key.pem",
            disableCustomTLSFirstByte: True,
        },
        quic: Client.Quicoptions {
            maxIncomingStreams: 100,
            maxIdleTimeout: 120,
            keepalivePeriod: 20,
        },
    },
    webServer: Client.WebServerConfig {
        addr: "0.0.0.0",
        port: 8080,
        user: "admin",
        password: "password123",
        assetsDir: "/var/www/assets",
        pprofEnable: True,
        tls: Client.Tlsconfig {
            serverName: "example.com",
            trustedCaFile: "/etc/tls/ca.pem",
            certFile: "/etc/tls/cert.pem",
            keyFile: "/etc/tls/key.pem",
        },
    },
}