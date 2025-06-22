import schemas.flux_kcl_controller.models.v1.source_toolkit_fluxcd_io_v1_git_repository as gitRepo
import schemas.flux_kcl_controller.models.v1alpha1.krm_kcl_dev_fluxcd_v1alpha1_k_c_l_run as kclRun
import manifests

settings = {
    name = "home-network"
    namespace = "default"
    repo_url = "https://github.com/awesome-kusion/kcl-deployment.git"
    repo_branch = "main"
    interval = "1m"
    path = "./configurations"
    prune = True
    # True to tell the reconcilier to not apply anything from the repo for a bit until you turn it back on
    suspend = False
    wait = True
}

repo = gitRepo.GitRepository {
    metadata.name = settings.name
    metadata.namespace = settings.namespace
    spec = {
        interval = settings.interval
        url = settings.repo_url
        ref.branch = settings.repo_branch
    }
}

kclrun = kclRun.KCLRun {
    metadata.name = settings.name
    metadata.namespace = settings.namespace
    spec = {
        interval = settings.interval
        sourceRef = {
            kind = "GitRepository"
            name = settings.name
            namespace = settings.namespace
        }
        path = settings.path
        prune = settings.prune
        suspend = settings.suspend
        wait = settings.wait
    }
}

manifests.yaml_stream([repo, kclrun])