import fluxcd_helm_controller.v2.helm_toolkit_fluxcd_io_v2_helm_release as fluxcd

fluxcd.HelmRelease {
  metadata.name = "traefik"
  metadata.namespace = "traefik"

  spec = {
    interval = "10m"
    chart = {
      spec = {
        chart = "traefik"
        version = "21.2.0"
        sourceRef = {
          kind = "HelmRepository"
          name = "traefik"
          namespace = "traefik"
        }
      }
    }
    install = {
      createNamespace = True
    }
    values = {
      additionalArguments = [
        "--entryPoints.web.address=:80",
        "--entryPoints.websecure.address=:443"
      ]
    }
  }
}