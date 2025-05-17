export const PROJECT_ROOT = process.cwd(); // use cwd as "project root"
export const PHASES_DIR = `${PROJECT_ROOT}/phases`;
export const KUBECONFIG_DIR = `${PROJECT_ROOT}/kubeconfigs`;

export const CLUSTER_NAME = "home-lab";
export const K8S_ENDPOINT = "https://192.168.1.101:6443";

export const NODES = [
  { hostname: "top_rice-crispy-treat", ip: "192.168.1.101" },
  { hostname: "cp2", ip: "192.168.1.102" },
  { hostname: "cp3", ip: "192.168.1.103" },
];
