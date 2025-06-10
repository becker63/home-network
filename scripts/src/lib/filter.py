from typing import Any, TypeAlias
from pathlib import Path
import pytest

from configuration import FILTERS, ProjectFilters, KFile

TestCase: TypeAlias = Any  # pytest.param(...)

def filter_kcl_files(
    all_files: list[KFile],
    *filters: ProjectFilters,
) -> list[TestCase]:
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
