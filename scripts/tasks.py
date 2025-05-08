from invoke.collection import Collection
from sopsy_tasks import sopsy_tasks

ns = Collection()

# Add sopsy tasks under `sopsy.*`
ns.add_collection(Collection.from_module(sopsy_tasks), name="sopsy")
