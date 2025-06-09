# kcl_tasks/parametizer.py

from typing import Any, TypeAlias
from pathlib import Path
from configuration import FILTERS, ProjectFilters, KFile
from lib.find_kcl_files import find_kcl_files
import pytest

_all_kcl_files_cache: list[KFile] | None = None

def get_all_kcl_files_once() -> list[KFile]:
    global _all_kcl_files_cache
    if _all_kcl_files_cache is None:
        _all_kcl_files_cache = find_kcl_files(glob_pattern="*")
    return _all_kcl_files_cache


TestCase: TypeAlias = Any  # pytest.param(...)

def filter_kcl_files(
    *filters: ProjectFilters,
) -> list[TestCase]:
    all_files = get_all_kcl_files_once()
    seen_paths: set[Path] = set()
    cases: list[TestCase] = []

    for pf in filters:
        filter_fn = FILTERS[pf]
        for kf in all_files:
            if not filter_fn(kf) or kf.path in seen_paths:
                continue
            seen_paths.add(kf.path)
            cases.append(pytest.param(pf, kf, id=f"{pf.value}::{kf.path.stem}"))
    return cases
