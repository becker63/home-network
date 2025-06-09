# This is a little magic file that pytest looks for to know where tests are


from pathlib import Path
from typing import List
import pytest
from _pytest.config import Config
from _pytest.nodes import Item

def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    for item in items:
        file_path = Path(item.fspath)
        if "automation" in file_path.parts:
            item.add_marker(pytest.mark.automation)
        elif "check" in file_path.parts:
            item.add_marker(pytest.mark.check)
        elif "e2e" in file_path.parts:
            item.add_marker(pytest.mark.e2e)


from lib.find_kcl_files import find_kcl_files
from configuration import KFile

@pytest.fixture(scope="session")
def all_kcl_project_files() -> list[KFile]:
    # Glob everything, no suffix filter yet
    return find_kcl_files(glob_pattern="*", print_debug=False)
