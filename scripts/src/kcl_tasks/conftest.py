from pathlib import Path
from typing import List, cast

import pytest
from _pytest.config import Config
from _pytest.nodes import Item

from configuration import KFile
from lib.find_kcl_files import find_kcl_files
from lib.filter import filter_kcl_files

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
    # Explicit setattr to please Pyright
    setattr(config, "_kcl_all_files", find_kcl_files())

def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    filter_marker = getattr(metafunc.function, "_kcl_filter", None)
    if filter_marker and "pf" in metafunc.fixturenames and "kf" in metafunc.fixturenames:
        all_files = cast("list[KFile]", getattr(metafunc.config, "_kcl_all_files", []))
        metafunc.parametrize("pf,kf", filter_kcl_files(all_files, filter_marker))
