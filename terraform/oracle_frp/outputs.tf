output "frp_instance_ip" {
  value = oci_core_instance.frp_instance.public_ip
}
