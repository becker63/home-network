from pathlib import Path
from typing import List, cast

import pytest
from _pytest.config import Config
from _pytest.nodes import Item

from configuration import KFile
from lib.find_kcl_files import find_kcl_files
from lib.filter import find_unique_kfiles_by_types, filter_kcl_files, FILTERS


def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    for item in items:
        file_path = Path(item.fspath)
        if "automation" in file_path.parts:
            item.add_marker(pytest.mark.automation)
        elif "check" in file_path.parts:
            item.add_marker(pytest.mark.check)
        elif "e2e" in file_path.parts:
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
def all_kcl_files() -> list[KFile]:
    return find_kcl_files()


def pytest_configure(config: Config) -> None:
    setattr(config, "_kcl_all_files", find_kcl_files())  # For use in parametrize hook


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    config_files = cast("list[KFile]", getattr(metafunc.config, "_kcl_all_files", []))

    # 1. Single-file test filtering via ProjectFilters
    filter_marker = getattr(metafunc.function, "_kcl_filter", None)
    if filter_marker and "pf" in metafunc.fixturenames and "kf" in metafunc.fixturenames:
        metafunc.parametrize("pf,kf", filter_kcl_files(config_files, filter_marker))

    # 2. Grouped-file tests via type string + ProjectFilters
    group_types = getattr(metafunc.function, "_kcl_group_types", None)
    group_filter = getattr(metafunc.function, "_kcl_group_filter", None)
    if group_types and group_filter:
        filter_fn = FILTERS[group_filter]
        filtered_files = [kf for kf in config_files if filter_fn(kf)]

        file_map = find_unique_kfiles_by_types(group_types, filtered_files)

        argnames = [f"{t.lower()}_kf" for t in group_types]
        argvalues = [file_map[t] for t in group_types]

        metafunc.parametrize(argnames, [argvalues], ids=["::".join(argnames)])
