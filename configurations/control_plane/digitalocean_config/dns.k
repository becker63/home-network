import schemas.digitalocean.models.v1alpha1.dns_digitalocean_crossplane_io_v1alpha1_domain as do_domain
import schemas.digitalocean.models.v1alpha1.dns_digitalocean_crossplane_io_v1alpha1_record as do_record
import k8s.apimachinery.pkg.apis.meta.v1 as meta

domain = "becker63.cloud"

schema DNSResource:
    name: str
    base: do_domain.Domain | do_record.Record

dns_resources = lambda ip: str {
    resources: [DNSResource] = [
        DNSResource {
            name = "create-domain"
            base = do_domain.Domain {
                metadata = meta.ObjectMeta {
                    name = "becker63-cloud"
                }
                spec = {
                    forProvider = {
                        name = domain
                        ipAddress = str(ip)
                    }
                    providerConfigRef = {
                        name = "default"
                    }
                }
            }
        },
        DNSResource {
            name = "dns-frps"
            base = do_record.Record {
                metadata = meta.ObjectMeta {
                    name = "frps-record"
                }
                spec = {
                    forProvider = {
                        name = "frps"
                        domain = domain
                        $type = "A"
                        ttl = 300
                        value = ip
                    }
                    providerConfigRef = {
                        name = "default"
                    }
                }
            }
        },
        DNSResource {
            name = "dns-headlamp"
            base = do_record.Record {
                metadata = meta.ObjectMeta {
                    name = "headlamp-record"
                }
                spec = {
                    forProvider = {
                        name = "headlamp"
                        domain = domain
                        $type = "A"
                        ttl = 300
                        value = str(ip)
                    }
                    providerConfigRef = {
                        name = "default"
                    }
                }
            }
        }
    ]

    # Convert schema objects to plain dicts
    [ { name = r.name, base = r.base } for r in resources ]
}