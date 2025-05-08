from invoke.collection import Collection
import sys
from pathlib import Path

# Use your project root detection
from root_config import find_project_root

PROJECT_ROOT = find_project_root(Path(__file__).resolve())

BOOTSTRAP_TASKS_PATH = PROJECT_ROOT / "phases" / "0-bootstrap" / "scripts" / "talos_home_main"
sys.path.insert(0, str(BOOTSTRAP_TASKS_PATH))

# gross crap we gotta do to import from the sopsy_tasks folder
from sopsy_tasks import sopsy_tasks
import bootstrap_tasks

ns = Collection()
ns.add_collection(Collection.from_module(sopsy_tasks), name="sopsy")
ns.add_collection(Collection.from_module(bootstrap_tasks), name="home_cluster")
