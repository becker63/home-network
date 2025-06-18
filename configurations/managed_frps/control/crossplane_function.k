import schemas.crossplane_composistion.models.v1 as cross
import schemas.crossplane_patch_and_transform.models.v1beta1.pt_fn_crossplane_io_v1beta1_resources as patch
import schemas.crossplane_sequencer.models.v1beta1.sequencer_fn_crossplane_io_v1beta1_input as seq
import schemas.python_crossplane_function.models.v1beta1.python_fn_crossplane_io_v1beta1_script as pyfn
import file

import crossplane_provider_upjet_gcp.v1beta1.compute_gcp_upbound_io_v1beta1_instance as gcp_instance
import crossplane_provider_upjet_gcp.v1beta1.compute_gcp_upbound_io_v1beta1_image as gcp_image
import crossplane_provider_upjet_gcp.v1beta1.storage_gcp_upbound_io_v1beta1_bucket as gcs_bucket
import crossplane_provider_upjet_gcp.v1beta1.storage_gcp_upbound_io_v1beta1_bucket_object as gcs_object
import crossplane_provider_upjet_gcp.v1beta1.storage_gcp_upbound_io_v1beta1_bucket_i_a_m_member as gcs_iam

settings = {
    instanceName = "frps-nixos-latest"
    imageName = "frps-nixos-latest-image"
    bucketObjectName = "frps-nixos-latest-image.qcow2"
    bucketName = "frps-tmp-image-store"
    projectId = "your-gcp-project-id"
    zone = "us-central1-a"
    machineType = "e2-micro"
    tags = ["frps"]
}

patch_resource = patch.Resources {
    metadata.name = "patch-transform-resources"
    resources = [
        {
            name = "create-bucket"
            base = gcs_bucket.Bucket {
                metadata.name = settings.bucketName
                spec = {
                    deletionPolicy = "Delete"
                    forProvider = {
                        location = "US"
                        project = settings.projectId
                        uniformBucketLevelAccess = True
                    }
                    providerConfigRef.name = "default"
                }
            }
        },
        {
            name = "grant-object-access"
            base = gcs_iam.BucketIAMMember {
                metadata.name = settings.bucketName + "-viewer-iam"
                spec = {
                    forProvider = {
                        bucket = settings.bucketName
                        role = "roles/storage.objectViewer"
                        member = "serviceAccount:${settings.projectId}@appspot.gserviceaccount.com"
                    }
                    providerConfigRef.name = "default"
                }
            }
        },
        {
            name = "upload-image"
            base = gcs_object.BucketObject {
                metadata.name = settings.bucketObjectName
                spec = {
                    forProvider = {
                        bucket = settings.bucketName
                        name = settings.bucketObjectName
                        source = "https://example.com/images/${settings.bucketObjectName}"
                    }
                    providerConfigRef.name = "default"
                    deletionPolicy = "Delete"
                }
            }
        },
        {
            name = "register-image"
            base = gcp_image.Image {
                metadata.name = settings.imageName
                spec = {
                    forProvider = {
                        rawDisk = [{
                            source = "https://storage.googleapis.com/${settings.bucketName}/${settings.bucketObjectName}"
                        }]
                        storageLocations = ["us"]
                        project = settings.projectId
                    }
                    providerConfigRef.name = "default"
                }
            }
        },
        {
            name = "launch-instance"
            base = gcp_instance.Instance {
                metadata.name = settings.instanceName
                spec = {
                    forProvider = {
                        zone = settings.zone
                        machineType = settings.machineType
                        bootDisk = [{
                            initializeParams = [{
                                image = ""
                            }]
                        }]
                        networkInterface = [{
                            network = "default"
                        }]
                        tags = settings.tags
                    }
                    providerConfigRef.name = "default"
                }
            }
            patches = [
                {
                    fromFieldPath = "imageName"
                    toFieldPath = "spec.forProvider.bootDisk[0].initializeParams[0].image"
                    type = "FromCompositeFieldPath"
                    transforms = [
                        {
                            type = "string"
                            string = {
                                type = "Format"
                                fmt = "projects/${settings.projectId}/global/images/%s"
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

sequencer_input = seq.Input {
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

cleanup_function = pyfn.Script {
    script = file.read("function.py")
}

comp = cross.Composition {
  metadata.name = "frps-vps-pipeline"
  spec = {
    compositeTypeRef = { apiVersion = "infra.fn/v1alpha1" kind = "VPS" }
    mode = "Pipeline"
    pipeline = [
      { step = "patch-resources" functionRef.name = "patch-and-transform" input = patch_resource },
      { step = "sequencing" functionRef.name = "sequencer" input = sequencer_input },
      { step = "cleanup-upload-image" functionRef.name = "python-function" input = cleanup_function }
    ]
  }
}