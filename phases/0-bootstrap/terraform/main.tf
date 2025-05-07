module "oracle_frp" {
  source = "./oracle_frp"
}

output "oracle_frp_ip" {
  value = module.oracle_frp.frp_instance_ip
}
