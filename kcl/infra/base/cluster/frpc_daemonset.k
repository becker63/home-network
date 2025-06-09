import k8s.api.apps.v1 as apps
import k8s.api.core.v1 as core
import infra.base.proxy.FRPC_Config as frpc
import json
import manifests

configs = [core.ConfigMap {
    metadata: {
        name: "frpc-config"
        namespace: "kube-system"
    }
    data: {
        "frpc.json": json.encode(frpc.config)
    }
}]

# Single DaemonSet that runs on all nodes
main = [apps.DaemonSet {
    metadata: {
        name: "frpc-daemonset"
        namespace: "kube-system"
        labels: {
            app: "frpc"
        }
    }
    spec: {
        updateStrategy: {
            "type": "RollingUpdate"
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
                    image: "snowdreamtech/frpc:v0.58.0"
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
                        mountPath: "/etc/frpc/frpc.json"
                        subPath: "frpc.json"
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
manifests.yaml_stream(main + sets)
