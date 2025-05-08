output "frp_node_ips" {
  value = [for d in digitalocean_droplet.frp_nodes : d.ipv4_address]
}
