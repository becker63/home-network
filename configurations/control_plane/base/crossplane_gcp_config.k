import crossplane.v1.pkg_crossplane_io_v1_provider as pkg
import k8s.apimachinery.pkg.apis.meta.v1 as meta
import crossplane_provider_upjet_gcp.v1beta1.gcp_upbound_io_v1beta1_provider_config as gcpconfig
import meta.prefilled_infisical_secret as I
import manifests

# --- GCP Provider Installation ---
gcp_provider = pkg.Provider {
    metadata = meta.ObjectMeta {
        name = "provider-gcp"
    }
    spec = {
        package = "xpkg.crossplane.io/crossplane-contrib/provider-gcp:v1.14.0"
    }
}

# --- InfisicalSecret to provision "gcp-creds" secret from Infisical ---
gcp_creds_secret = I.InfisicalSecret {
    slug = "gcp-creds"
    namespace = "crossplane-system"
    keys = {
        "GCP_CREDS_JSON": "creds"
    }
}

# --- GCP ProviderConfig: Reference secret managed by Infisical ---
gcp_config = gcpconfig.ProviderConfig {
    metadata = meta.ObjectMeta {
        name = "gcp-provider-config"
    }
    spec = {
        projectID = "your-gcp-project-id"  # Replace with your actual GCP project ID
        credentials = {
            source = "Secret"
            secretRef = {
                namespace = "crossplane-system"
                name = "gcp-creds"
                key = "creds"
            }
        }
    }
}

manifests.yaml_stream([
    gcp_provider,
    gcp_config,
    gcp_creds_secret.secret
])