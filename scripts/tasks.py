from invoke.collection import Collection
from talos_home_main import ns as bootstrap_ns
from sopsy_tasks import sopsy_tasks

ns = Collection()

# Add bootstrap tasks under `bootstrap.*`
ns.add_collection(bootstrap_ns, name="talos")

# Add sopsy tasks under `sopsy.*`
ns.add_collection(Collection.from_module(sopsy_tasks), name="sopsy")
