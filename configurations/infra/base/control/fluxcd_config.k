import fluxcd_kustomize_controller.v1 as kustomize
import fluxcd_source_controller.v1beta2.source_toolkit_fluxcd_io_v1beta2_git_repository as fluxcd
import k8s.apimachinery.pkg.apis.meta.v1 as meta
import manifests

# GitRepository: watches the full repo
fluxrepo = fluxcd.GitRepository {
    metadata = meta.ObjectMeta {
        name = "home-network"
        namespace = "flux-system"
    }
    spec = {
        url = "https://github.com/becker63/home-network"
        interval = "1m"
        ref = {
            branch = "main"
        }
    }
}

# Kustomization: only applies manifests from ./synth_yaml
fluxkust = kustomize.Kustomization {
    metadata = meta.ObjectMeta {
        name = "apply-synth"
        namespace = "flux-system"
    }
    spec = {
        interval = "1m"
        sourceRef = {
            kind = "GitRepository"
            name = "home-network"
        }
        path = "./synth_yaml"
        prune = True
        targetNamespace = "default"
    }
}

manifests.yaml_stream([fluxrepo, fluxkust])