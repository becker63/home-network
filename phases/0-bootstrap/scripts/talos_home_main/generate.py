from invoke.tasks import task
import yaml
from config import (
    CLUSTER_NAME,
    K8S_ENDPOINT,
    NODES,
    CONFIG_DIR,
)

@task
def generate_config(c):
    """
    Generate Talos cluster config and per-node machine configs.
    """
    print(f"📦 Generating Talos config in {CONFIG_DIR}")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    result = c.run(
        f"talosctl gen config {CLUSTER_NAME} {K8S_ENDPOINT} --output-dir {CONFIG_DIR} --force",
        echo=True,
        warn=True
    )

    if result.failed:
        print("❌ talosctl gen config failed.")
        return

    template_path = CONFIG_DIR / "controlplane.yaml"
    if not template_path.exists():
        print("❌ controlplane.yaml not found.")
        return

    with template_path.open() as f:
        controlplane_template = yaml.safe_load(f)

    for node in NODES:
        config = controlplane_template.copy()
        config["machine"]["network"] = {
            "interfaces": [{
                "interface": "eth0",
                "addresses": [f"{node['ip']}/24"],
                "dhcp": False,
            }],
            "hostname": node["hostname"]
        }

        output_path = CONFIG_DIR / f"{node['hostname']}.yaml"
        with output_path.open("w") as f:
            yaml.dump(config, f)

        print(f"✅ Wrote config: {output_path}")
