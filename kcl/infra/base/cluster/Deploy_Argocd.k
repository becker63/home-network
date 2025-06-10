import argo_cd.v1alpha1 as Argo
import manifests

argo_app = Argo.Application {
    metadata.name = "example-app"
    metadata.namespace = "argocd"
    spec.project = "default"

    spec.source.repoURL = "https://github.com/example/repo.git"
    spec.source.targetRevision = "HEAD"
    spec.source.path = "manifests/app"

    spec.destination.server = "https://kubernetes.default.svc"
    spec.destination.namespace = "default"

    spec.syncPolicy.automated.prune = True
    spec.syncPolicy.automated.selfHeal = True

    spec.source.helm.values = """
      secretName: repo-creds
    """
}

manifests.yaml_stream(argo_app)
