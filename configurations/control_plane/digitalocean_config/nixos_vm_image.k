import schemas.crossplane_composistion.models.v1 as cross
import schemas.crossplane_patch_and_transform.models.v1beta1.pt_fn_crossplane_io_v1beta1_resources as patch
import schemas.crossplane_sequencer.models.v1beta1.sequencer_fn_crossplane_io_v1beta1_input as seq

import schemas.digitalocean.models.v1alpha1.droplet_digitalocean_crossplane_io_v1alpha1_droplet as do_droplet
import schemas.digitalocean.models.v1alpha1.custom_digitalocean_crossplane_io_v1alpha1_image as do_image

settings = {
    dropletName = "frps-nixos-droplet"
    imageName = "frps-nixos-custom"
    region = "nyc3"
    size = "s-1vcpu-1gb"
    imageUrl = "https://your-public-host/frps-nixos-latest.qcow2"
}

patch_resource = patch.Resources {
    metadata.name = "patch-digitalocean-resources"
    resources = [
        {
            name = "create-image"
            base = do_image.Image {
                metadata.name = settings.imageName
                spec = {
                    forProvider = {
                        name = settings.imageName
                        url = settings.imageUrl
                        distribution = "nixos-frps"
                    }
                    providerConfigRef.name = "default"
                }
            }
        },
        {
            name = "create-droplet"
            base = do_droplet.Droplet {
                metadata.name = settings.dropletName
                spec = {
                    forProvider = {
                        name = settings.dropletName
                        region = settings.region
                        size = settings.size
                        image = settings.imageName
                        monitoring = True
                    }
                    providerConfigRef.name = "default"
                }
            }
        }
    ]
}

sequencer_input = seq.Input {
    metadata.name = "execution-sequence"
    rules = [
        {
            sequence = [
                "create-image"
                "create-droplet"
            ]
        }
    ]
}

comp = cross.Composition {
    metadata.name = "frps-digitalocean-vps-pipeline"
    spec = {
        compositeTypeRef = {
            apiVersion = "infra.fn/v1alpha1"
            kind = "VPS"
        }
        mode = "Pipeline"
        pipeline = [
            {
                step = "patch-digitalocean"
                functionRef.name = "patch-and-transform"
                input = patch_resource
            },
            {
                step = "sequence"
                functionRef.name = "sequencer"
                input = sequencer_input
            }
        ]
    }
}