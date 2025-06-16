import fluxcd_helm_controller.v2.helm_toolkit_fluxcd_io_v2_helm_release as fluxcd_release

fluxcd_release.HelmRelease {
  metadata.name = "cert-manager"
  metadata.namespace = "cert-manager"

  spec = {
    interval = "10m"
    chart = {
      spec = {
        chart = "cert-manager"
        version = "v1.14.5"  # adjust as needed
        sourceRef = {
          kind = "HelmRepository"
          name = "jetstack"
          namespace = "cert-manager"
        }
      }
    }
    install = {
      createNamespace = True
    }
    values = {
      installCRDs = True
    }
  }
}