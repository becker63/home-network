import schemas.digitalocean.models.v1alpha1.droplet_digitalocean_crossplane_io_v1alpha1_droplet as do_droplet
import schemas.digitalocean.models.v1alpha1.custom_digitalocean_crossplane_io_v1alpha1_image as do_image
import k8s.apimachinery.pkg.apis.meta.v1 as meta

settings_vm = {
    dropletName = "frps-nixos-droplet"
    imageName = "frps-nixos-custom"
    region = "nyc3"
    size = "s-1vcpu-1gb"
    imageUrl = "https://your-public-host/frps-nixos-latest.qcow2"
    provider = "default"
}

schema VMResource:
    name: str
    base: do_image.Image | do_droplet.Droplet

vm_resources = [
    VMResource {
        name = "create-image"
        base = do_image.Image {
            metadata.name = settings_vm.imageName
            spec = {
                forProvider = {
                    name = settings_vm.imageName
                    url = settings_vm.imageUrl
                    distribution = "nixos-frps"
                }
                providerConfigRef.name = settings_vm.provider
            }
        }
    },
    VMResource {
        name = "create-droplet"
        base = do_droplet.Droplet {
            metadata.name = settings_vm.dropletName
            spec = {
                forProvider = {
                    name = settings_vm.dropletName
                    region = settings_vm.region
                    size = settings_vm.size
                    image = settings_vm.imageName
                    monitoring = True
                }
                providerConfigRef.name = settings_vm.provider
            }
        }
    }
]

vm_resource_objects = [ { name = r.name, base = r.base } for r in vm_resources ]