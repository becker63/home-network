import k8s.api.apps.v1 as apps
import k8s.api.core.v1 as core
import manifests

# TODO: write a kuttl integration test for this, will need to use functions/abstractions to have a polymorphic test version and prod version
# see: https://www.kcl-lang.io/docs/user_docs/support/faq-kcl#21-how-to-write-configuration-based-on-schema-how-to-reuse-the-common-configuration-between-multiple-configurations
# and: https://github.com/kcl-lang/examples/tree/main/abstraction
#           /\
#           ||
# In fact this might actually be better for this dynamic use case with nodes. Nodes should be a schema.

# Realistically though we're using pytest. For testing we can just overide the port/ip information. ALSO: we might not need to integration test frp.

frpc_toml = '''
[common]
server_addr = "frps.example.com"
server_port = 7000
token = "your-shared-token"

[headlamp]
type = http
local_ip = headlamp.kube-system.svc.cluster.local
local_port = 80
remote_port = 30080
custom_domains = headlamp.example.com

group = headlamp
group_key = your-shared-key
health_check_type = http
health_check_url = /
health_check_interval_s = 10
health_check_timeout_s = 3
health_check_max_failed = 3
'''
# /\ in actual code we'll type this

configs = [core.ConfigMap {
    metadata: {
        name: "frpc-config"
        namespace: "kube-system"
    }
    data: {
        "frpc.toml": frpc_toml
    }
}]

# Single DaemonSet that runs on all nodes
sets = [apps.DaemonSet {
    metadata: {
        name: "frpc-daemonset"
        namespace: "kube-system"
        labels: {
            app: "frpc"
        }
    }
    spec: {
        updateStrategy: {
            type: "RollingUpdate"
        }
        selector: {
            matchLabels: {
                app: "frpc"
            }
        }
        template: {
            metadata: {
                labels: {
                    app: "frpc"
                }
            }
            spec: {
                hostNetwork: True
                containers: [{
                    name: "frpc"
                    image: "snowdreamtech/frpc"
                    env: [{
                        name: "NODE_NAME"
                        valueFrom: {
                            fieldRef: {
                                fieldPath: "spec.nodeName"
                            }
                        }
                    }]
                    volumeMounts: [{
                        name: "config-volume"
                        mountPath: "/etc/frpc/frpc.toml"
                        subPath: "frpc.toml"
                    }]
                    command: ["/entrypoint.sh"]
                }]
                volumes: [{
                    name: "config-volume"
                    configMap: {
                        name: "frpc-config"
                    }
                }]
            }
        }
    }
}]

# Emit both ConfigMap and DaemonSet
manifests.yaml_stream(configs + sets)
