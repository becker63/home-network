from invoke.collection import Collection
from bootstrap_talos import bootstrap_tasks
from sopsy_tasks import sopsy_tasks

ns = Collection()

# Add bootstrap tasks under `bootstrap.*`
ns.add_collection(Collection.from_module(bootstrap_tasks), name="bootstrap")

# Add sopsy tasks under `sopsy.*`
ns.add_collection(Collection.from_module(sopsy_tasks), name="sopsy")
