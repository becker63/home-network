import schemas.traefik.models.v1alpha1.traefik_io_v1alpha1_ingress_route as traefik
import schemas.traefik.models.v1alpha1.traefik_io_v1alpha1_middleware as middleware
import k8s.apimachinery.pkg.apis.meta.v1 as meta
import manifests

auth_middleware = middleware.Middleware {
    metadata = meta.ObjectMeta {
        name = "auth-forward"
        namespace = "default"
    }
    spec = {
        forwardAuth = {
            address = "http://oauth2-proxy.default.svc.cluster.local:4180"  # Adjust as needed
            trustForwardHeader = True
            authResponseHeaders = ["X-Auth-Request-User", "X-Auth-Request-Email"]
        }
    }
}

route = traefik.IngressRoute {
    metadata = meta.ObjectMeta {
        name = "headlamp-http"
        namespace = "default"
    }
    spec = {
        entryPoints = ["web"]
        routes = [{
            match = "Host(`headlamp.example.com`)"
            kind = "Rule"
            services = [{
                name = "headlamp"
                port = 80
            }]
            middlewares = [{
                name = "auth-forward"
                namespace = "default"
            }]
        }]
    }
}

manifests.yaml_stream([auth_middleware, route])