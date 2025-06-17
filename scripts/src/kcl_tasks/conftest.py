from typing import cast

import pytest
from _pytest.config import Config

from configuration import KFile
from lib.find_kcl_files import find_kcl_files
from lib.filter import filter_kcl_files


@pytest.fixture(scope="session")
def all_kcl_files() -> list[KFile]:
    return find_kcl_files()


def pytest_configure(config: Config) -> None:
    setattr(config, "_kcl_all_files", find_kcl_files())


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    config_files = cast("list[KFile]", getattr(metafunc.config, "_kcl_all_files", []))

    # --- Case 1: Single-file test filtering ---
    filter_marker = getattr(metafunc.function, "_kcl_filter", None)
    if filter_marker and "pf" in metafunc.fixturenames and "kf" in metafunc.fixturenames:
        metafunc.parametrize("pf,kf", filter_kcl_files(config_files, filter_marker))
        return

    # --- Case 2: Grouped substring matching ---
    raw_substrs = getattr(metafunc.function, "_kcl_group_substrs", None)
    group_filter = getattr(metafunc.function, "_kcl_group_filter", None)

    if not isinstance(raw_substrs, list) or not all(isinstance(s, str) for s in raw_substrs):
        return  # Not applicable for this test

    if group_filter is None:
        raise ValueError(f"{metafunc.function.__name__} is missing _kcl_group_filter")

    # Apply filter and extract raw KFile values from param sets
    filtered_params = filter_kcl_files(config_files, group_filter)
    filtered_kfiles = [param.values[1] for param in filtered_params]

    matched: list[KFile] = []
    for substr in raw_substrs:
        match = next(
            (kf for kf in filtered_kfiles if substr in kf.path.read_text(encoding="utf-8")),
            None
        )
        if not match:
            raise ValueError(f"No match for '{substr}' in contents of filtered KCL files.")
        matched.append(match)

    # Use function parameter names in order (e.g. "clientconfig_kf", "serverconfig_kf", ...)
    argnames = metafunc.function.__code__.co_varnames[:len(matched)]
    metafunc.parametrize(argnames, [matched], ids=["::".join(argnames)])
