// tasks.ts
// TODO: Move to omni with net boot
import { $ } from "zx";
import * as fs from "fs";
import * as path from "path";
import yaml from "js-yaml";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// ---- Placeholder Config Constants ----

const CONFIG_DIR = path.resolve(__dirname, "./talosctl/bootstrap_config");
const TALOSCONFIG_PATH = path.join(CONFIG_DIR, "talosconfig");
const KUBECONFIG_PATH = path.resolve(
  __dirname,
  "./kubeconfigs/home_kubeconfig.yaml",
);

const CLUSTER_NAME = "home-lab";
const K8S_ENDPOINT = "https://192.168.1.101:6443";

const NODES = [
  { hostname: "top_rice-crispy-treat", ip: "192.168.1.101" },
  { hostname: "cp2", ip: "192.168.1.102" },
  { hostname: "cp3", ip: "192.168.1.103" },
];

// ---- Helper Functions ----

function getBootstrapNodeIP(): string {
  return NODES[0].ip;
}

function resolveHostname(ip: string): string {
  const node = NODES.find((n) => n.ip === ip);
  return node ? node.hostname : "unknown";
}

// ---- ZX Tasks ----

export async function bootstrapCluster() {
  const nodeIp = getBootstrapNodeIP();
  console.log(`🚀 Bootstrapping from ${nodeIp}`);
  await $`talosctl bootstrap --talosconfig ${TALOSCONFIG_PATH} --nodes ${nodeIp} --endpoints ${nodeIp}`;
}

export async function fetchKubeconfig(force = false) {
  const nodeIp = getBootstrapNodeIP();
  console.log(`📦 Fetching kubeconfig from ${nodeIp}`);
  const forceFlag = force ? "--force" : "";
  await $`talosctl kubeconfig --talosconfig ${TALOSCONFIG_PATH} --nodes ${nodeIp} --endpoints ${nodeIp} ${forceFlag} ${KUBECONFIG_PATH}`;
}

export async function applyConfig(nodeIp: string) {
  const hostname = resolveHostname(nodeIp);
  const configFile = path.join(CONFIG_DIR, `${hostname}.yaml`);
  console.log(`📦 Applying config to ${nodeIp}`);
  await $`talosctl apply-config --insecure --nodes ${nodeIp} --file ${configFile}`;
}

export async function healthCheck() {
  const ip = getBootstrapNodeIP();
  console.log("🔍 Checking health of cluster.");
  await $`talosctl health --talosconfig ${TALOSCONFIG_PATH} --nodes ${ip} --endpoints ${ip}`;
}

export async function generateConfig() {
  console.log(`📦 Generating Talos config in ${CONFIG_DIR}`);
  fs.mkdirSync(CONFIG_DIR, { recursive: true });

  const result =
    await $`talosctl gen config ${CLUSTER_NAME} ${K8S_ENDPOINT} --output-dir ${CONFIG_DIR} --force`.nothrow();

  if (result.exitCode !== 0) {
    console.error("❌ talosctl gen config failed.");
    return;
  }

  const templatePath = path.join(CONFIG_DIR, "controlplane.yaml");
  if (!fs.existsSync(templatePath)) {
    console.error("❌ controlplane.yaml not found.");
    return;
  }

  const controlplaneTemplate = yaml.load(
    fs.readFileSync(templatePath, "utf8"),
  ) as any;

  for (const node of NODES) {
    const config = JSON.parse(JSON.stringify(controlplaneTemplate)); // deep copy
    config.machine.network = {
      interfaces: [
        {
          interface: "eth0",
          addresses: [`${node.ip}/24`],
          dhcp: false,
        },
      ],
      hostname: node.hostname,
    };

    const outputPath = path.join(CONFIG_DIR, `${node.hostname}.yaml`);
    fs.writeFileSync(outputPath, yaml.dump(config));
    console.log(`✅ Wrote config: ${outputPath}`);
  }
}
