terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "frp_nodes" {
  count  = 2
  name   = "frp-node-${count.index + 1}"
  region = "nyc1"
  size   = "s-1vcpu-512mb-10gb" # cheapest tier
  image  = "ubuntu-22-04-x64"

  ssh_keys = [
    var.ssh_key_fingerprint
  ]
}
