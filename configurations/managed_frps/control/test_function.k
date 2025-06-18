import crossplane.v1 as pkg
import schemas.crossplane_composistion.models.v1 as cross
import schemas.crossplane_patch_and_transform.models.v1beta1.pt_fn_crossplane_io_v1beta1_resources as patch
import schemas.crossplane_sequencer.models.v1beta1.sequencer_fn_crossplane_io_v1beta1_input as seq
import schemas.python_crossplane_function.models.v1beta1.python_fn_crossplane_io_v1beta1_script as pyfn
import k8s.apimachinery.pkg.apis.meta.v1 as meta
import manifests
import file

mock_input = patch.Resources {
    metadata.name = "mock-input"
    resources = [
        {
            name = "upload-image"
            base.apiVersion = "mock.crossplane.io/v1"
            base.kind = "UploadImage"
        }
        {
            name = "launch-instance"
            base.apiVersion = "nop.crossplane.io/v1alpha1"
            base.kind = "NopResource"
            base.spec.forProvider.conditionAfter = [{
                time = "3s"
                conditionType = "Ready"
                conditionStatus = "True"
            }]
            readinessChecks = [{
                type = "MatchCondition"
                matchCondition = {
                    type = "Ready"
                    status = "True"
                }
            }]
        }
    ]
}

mock_sequence = seq.Input {
    metadata.name = "mock-seq"
    rules = [{
        sequence = ["upload-image", "launch-instance"]
    }]
}

cleanup_fn = pyfn.Script {
    metadata.name = "test-cleanup-script"
    metadata.namespace = "default"
    script = file.read("del_image.py")
}

python_function = pkg.Function {
    metadata.name = "python-function"
    spec = {
        package = "xpkg.upbound.io/upbound/function-python"
        runtimeConfigRef.name = "default"
    }
}

composition = cross.Composition {
    metadata.name = "test-cleanup-pipeline"
    spec = {
        compositeTypeRef = {
            apiVersion = "mock.crossplane.io/v1alpha1"
            kind = "XNop"
        }
        mode = "Pipeline"
        pipeline = [
            {step = "mock", functionRef.name = "patch-and-transform", input = mock_input}
            {step = "sequence", functionRef.name = "sequencer", input = mock_sequence}
            {step = "cleanup", functionRef.name = "python-function", input = cleanup_fn}
        ]
    }
}

xr = {
    apiVersion = "mock.crossplane.io/v1alpha1"
    kind = "XNop"
    metadata = {
        name = "test-cleanup-xnop"
        namespace = "default"
        annotations = {
            "crossplane.io/composition-resource-name": "test-cleanup-pipeline"
        }
    }
    spec.forProvider.conditionAfter = [{
        time = "1s"
        conditionType = "Ready"
        conditionStatus = "True"
    }]
}

manifests.yaml_stream([xr, python_function, cleanup_fn, composition])