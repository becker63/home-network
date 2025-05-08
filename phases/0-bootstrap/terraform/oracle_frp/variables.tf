variable "oracle_user_ocid" {
  type = string
}

variable "oracle_tenancy_ocid" {
  type = string
}

variable "oracle_fingerprint" {
  type = string
}

variable "oracle_private_key" {
  type      = string
  sensitive = true
}

variable "oracle_region" {
  type = string
}

variable "ssh_public_key" {
  type = string
}

variable "compartment_ocid" {
  type = string
}
