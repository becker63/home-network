provider "oci" {
  tenancy_ocid = var.oracle_tenancy_ocid
  user_ocid    = var.oracle_user_ocid
  fingerprint  = var.oracle_fingerprint
  private_key  = var.oracle_private_key
  region       = var.oracle_region
}

resource "oci_core_virtual_network" "bootstrap_vcn" {
  cidr_block     = "10.0.0.0/16"
  display_name   = "bootstrap-vcn"
  compartment_id = var.compartment_ocid
}

resource "oci_core_internet_gateway" "bootstrap_igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.bootstrap_vcn.id
  display_name   = "bootstrap-igw"
}

resource "oci_core_route_table" "bootstrap_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.bootstrap_vcn.id
  display_name   = "bootstrap-rt"

  route_rules {
    network_entity_id = oci_core_internet_gateway.bootstrap_igw.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_subnet" "bootstrap_subnet" {
  cidr_block                 = "10.0.1.0/24"
  display_name               = "bootstrap-subnet"
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_virtual_network.bootstrap_vcn.id
  route_table_id             = oci_core_route_table.bootstrap_rt.id
  prohibit_public_ip_on_vnic = false
}

resource "oci_core_instance" "bootstrap_vms" {
  count               = 2
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 1
    memory_in_gbs = 1
  }

  display_name = "bootstrap-vm-${count.index + 1}"

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.oracle_linux.id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.bootstrap_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  preserve_boot_volume = false
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.oracle_tenancy_ocid
}

data "oci_core_images" "oracle_linux" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}
