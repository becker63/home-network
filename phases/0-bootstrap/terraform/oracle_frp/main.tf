provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

# VCN
resource "oci_core_vcn" "frp_vcn" {
  compartment_id = var.compartment_id
  cidr_block     = "10.0.0.0/16"
  display_name   = "frp-vcn"
}

# Internet Gateway
resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.frp_vcn.id
  display_name   = "frp-internet-gateway"
}

# Route Table
resource "oci_core_route_table" "rt" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.frp_vcn.id
  display_name   = "frp-route-table"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.igw.id
  }
}

# Subnet
resource "oci_core_subnet" "frp_subnet" {
  compartment_id             = var.compartment_id
  vcn_id                     = oci_core_vcn.frp_vcn.id
  cidr_block                 = "10.0.0.0/24"
  display_name               = "frp-subnet"
  prohibit_public_ip_on_vnic = false
  route_table_id             = oci_core_route_table.rt.id
}

# Availability Domains
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

# Ubuntu ARM Image
data "oci_core_images" "oracle_arm" {
  compartment_id           = var.compartment_id
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = "VM.Standard.A1.Flex"
}

# Compute Instance
resource "oci_core_instance" "frp_instance" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_id
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 1
    memory_in_gbs = 1
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.oracle_arm.id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.frp_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }
}
