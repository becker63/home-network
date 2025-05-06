from invoke.collection import Collection
import talos.bootstrap_tasks as bootstrap
import talos.generate as generate
import talos.extra as extra

ns = Collection()
ns.add_collection(Collection.from_module(bootstrap))
ns.add_collection(Collection.from_module(generate))
ns.add_collection(Collection.from_module(extra))
