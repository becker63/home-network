from invoke.collection import Collection
import talos_home_main.bootstrap_tasks as bootstrap
import talos_home_main.generate as generate
import talos_home_main.extra as extra

ns = Collection()
ns.add_collection(Collection.from_module(bootstrap))
ns.add_collection(Collection.from_module(generate))
ns.add_collection(Collection.from_module(extra))
