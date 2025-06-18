import schemas.crossplane_composistion.models.v1 as cross
import schemas.crossplane_patch_and_transform.models.v1beta1.pt_fn_crossplane_io_v1beta1_resources as patch
import schemas.crossplane_sequencer.models.v1beta1.sequencer_fn_crossplane_io_v1beta1_input as seq
import schemas.python_crossplane_function.models.v1beta1.python_fn_crossplane_io_v1beta1_script as pyfn
import schemas.crossplane_nop.models.v1alpha1.nop_crossplane_io_v1alpha1_nop_resource as nop
import file
import manifests

settings_nop = {
    instanceName = "launch-instance"
    imageName = "test-image"
    bucketObjectName = "upload-image"
    provider = "provider-nop"
}

patch_resource_nop = patch.Resources {
    metadata.name = "patch-nop"
    resources = [
        {
            name = "create-bucket"
            base = nop.NopResource {
                metadata.name = "create-bucket"
                spec.forProvider = {
                    fields = {
                        purpose = "create-bucket"
                    }
                    conditionAfter = [{
                        time = "1s"
                        conditionType = "Ready"
                        conditionStatus = "True"
                    }]
                }
                spec.providerConfigRef.name = settings_nop.provider
            }
        },
        {
            name = "grant-object-access"
            base = nop.NopResource {
                metadata.name = "grant-access"
                spec.forProvider = {
                    fields = {
                        role = "objectViewer"
                    }
                    conditionAfter = [{
                        time = "1s"
                        conditionType = "Ready"
                        conditionStatus = "True"
                    }]
                }
                spec.providerConfigRef.name = settings_nop.provider
            }
        },
        {
            name = "upload-image"
            base = nop.NopResource {
                metadata.name = "upload-image"
                spec.forProvider = {
                    fields = {
                        type = "upload"
                    }
                    conditionAfter = [{
                        time = "2s"
                        conditionType = "Ready"
                        conditionStatus = "True"
                    }]
                }
                spec.providerConfigRef.name = settings_nop.provider
            }
        },
        {
            name = "register-image"
            base = nop.NopResource {
                metadata.name = "register-image"
                spec.forProvider = {
                    fields = {
                        image = "test-image"
                    }
                    conditionAfter = [{
                        time = "2s"
                        conditionType = "Ready"
                        conditionStatus = "True"
                    }]
                }
                spec.providerConfigRef.name = settings_nop.provider
            }
        },
        {
            name = "launch-instance"
            base = nop.NopResource {
                metadata.name = "launch-instance"
                spec.forProvider = {
                    fields = {
                        role = "vm"
                    }
                    conditionAfter = [{
                        time = "3s"
                        conditionType = "Ready"
                        conditionStatus = "True"
                    }]
                }
                spec.providerConfigRef.name = settings_nop.provider
            }
        }
    ]
}

sequencer_input_nop = seq.Input {
    metadata.name = "execution-sequence"
    rules = [
        {
            sequence = [
                "create-bucket"
                "grant-object-access"
                "upload-image"
                "register-image"
                "launch-instance"
            ]
        }
    ]
}

cleanup_function_nop = pyfn.Script {
    script = file.read("del_image.py")
}

comp_nop = cross.Composition {
    metadata.name = "nop-vps-test-pipeline"
    spec = {
        compositeTypeRef = {
            apiVersion = "infra.fn/v1alpha1"
            kind = "VPS"
        }
        mode = "Pipeline"
        pipeline = [
            {
                step = "patch-nop"
                functionRef.name = "patch-and-transform"
                input = patch_resource_nop
            },
            {
                step = "sequence"
                functionRef.name = "sequencer"
                input = sequencer_input_nop
            },
            {
                step = "cleanup"
                functionRef.name = "python-function"
                input = cleanup_function_nop
            }
        ]
    }
}

manifests.yaml_stream([comp_nop])