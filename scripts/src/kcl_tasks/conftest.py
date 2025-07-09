import pytest
from lib.test_ext.find_kcl_files import find_kcl_files
from lib.test_ext.find_proj_root import find_project_root
from pathlib import Path

def pytest_configure(config):
    root = find_project_root()
    config._kcl_all_files = find_kcl_files(root)

def pytest_generate_tests(metafunc):
    config_files = getattr(metafunc.config, "_kcl_all_files", [])

    filter_fn = getattr(metafunc.function, "_kcl_filter_fn", None)
    if callable(filter_fn) and "kf" in metafunc.fixturenames:
        matched = [kf for kf in config_files if filter_fn(kf)]

        if not matched:
            raise ValueError(f"No KCL files matched filter for {metafunc.function.__name__}")

        ids = [str(kf.path.relative_to(kf.path.parents[2])) for kf in matched]
        metafunc.parametrize("kf", matched, ids=ids)
