import sys
from pathlib import Path

# Add project root to PYTHONPATH dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from invoke.collection import Collection
from scripts.sopsy_tasks import sopsy_tasks
from phases.one_bootstrap.scripts.talos_home_main import bootstrap_tasks
from phases.one_bootstrap.scripts.generate_qcow import gen_qcow2_frp

ns = Collection()
ns.add_collection(Collection.from_module(sopsy_tasks), name="sopsy")
ns.add_collection(Collection.from_module(bootstrap_tasks), name="home_cluster")
ns.add_collection(Collection.from_module(gen_qcow2_frp), name="images")
