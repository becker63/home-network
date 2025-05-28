import schema.models.v1beta1 as Kutll
import k8s.apimachinery.pkg.apis.meta.v1


Kutll.TestStep {
    apiVersion = "kuttl.dev/v1beta1"
    kind = "TestStep"
    metadata = v1.ObjectMeta {
        name = "example-test-step"
        namespace = "testing"
    }
    apply = ["./manifests/deployment.yaml"]
    "$assert" = ["./asserts/check-deployment.yaml"]
    error = ["./errors/expected-fail.yaml"]
    delete = [
        {
            apiVersion = "v1"
            kind = "ConfigMap"
            metadata = {
                name = "obsolete-config"
                namespace = "testing"
            }
        }
    ]
    index = 1
    kubeconfig = "/home/user/.kube/test-kubeconfig"
    unitTest = False
    commands = [
        {
            command = "kubectl get pods"
            ignoreFailure = False
            namespaced = True
            skipLogOutput = False
            timeout = 15
        },
        {
            script = '''
                echo "Running test setup"
                export FOO=bar
                kubectl config get-contexts
            '''
            skipLogOutput = True
        }
    ]
}

Kutll.TestAssert {
    apiVersion = "kuttl.dev/v1beta1"
    kind = "TestAssert"
    metadata = v1.ObjectMeta {
        name = "example-test-assert"
        namespace = "testing"
    }
    timeout = 60
    collectors = {
        "$type" = "pod"
        pod = "test-pod"
        namespace = "testing"
        container = "app"
        tail = 20
    }
    commands = [
        {
            command = "kubectl logs test-pod"
            namespaced = True
            skipLogOutput = False
        },
        {
            script = '''
                if ! kubectl get svc my-service; then
                  echo "Service not found"
                  exit 1
                fi
            '''
            skipLogOutput = True
        }
    ]
}