import schemas.crossplane_composistion.models.v1 as cross
import schemas.crossplane_patch_and_transform.models.v1beta1.pt_fn_crossplane_io_v1beta1_resources as patch
import schemas.crossplane_sequencer.models.v1beta1.sequencer_fn_crossplane_io_v1beta1_input as seq
import manifests

import .nixos_frps_vm as vm
import .dns

params = option(
    key = "params",
    type = "dict",
    default = {
        ocds = {
            "create-droplet" = {
                Droplet = {
                    status = {
                        atProvider = {
                            ipv4Address = "FIXME!"
                        }
                    }
                }
            }
        }
    }
)

ip = params.ocds["create-droplet"].Droplet.status.atProvider.ipv4Address

patch_resource = patch.Resources {
    metadata.name = "patch-digitalocean-resources"
    resources = vm.vm_resource_objects + dns.dns_resources(ip)
}

sequencer_input = seq.Input {
    metadata.name = "execution-sequence"
    rules = [
        {
            sequence = [
                "create-image",
                "create-droplet",
                "create-domain",
                "dns-frps",
                "dns-headlamp"
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

manifests.yaml_stream([comp])