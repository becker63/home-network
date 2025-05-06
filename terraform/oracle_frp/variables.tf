variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string
}

variable "user_ocid" {
  description = "OCI user OCID"
  type        = string
}

variable "fingerprint" {
  description = "API key fingerprint"
  type        = string
}

variable "private_key_path" {
  description = "Path to your OCI private API key"
  type        = string
}

variable "region" {
  description = "OCI region (e.g., us-phoenix-1)"
  type        = string
}

variable "compartment_id" {
  description = "OCID of the compartment to deploy resources in"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key to access the instance"
  type        = string
}
