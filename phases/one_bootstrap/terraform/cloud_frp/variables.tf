variable "do_token" {
  type      = string
  sensitive = true
}

variable "ssh_key_fingerprint" {
  type        = string
  description = "The fingerprint of the uploaded SSH key in DigitalOcean"
}
