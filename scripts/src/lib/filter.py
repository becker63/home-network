from typing import Any, TypeAlias,List, Dict
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


def find_unique_kfiles_by_types(type_strs: List[str], all_kfiles: List[KFile]) -> Dict[str, KFile]:
    """
    Return a dict mapping each type string to the single KFile that defines it.

    Raises if any type has 0 or >1 matches.
    """
    result: Dict[str, KFile] = {}

    for type_str in type_strs:
        matches: List[KFile] = []

        for kf in all_kfiles:
            file_text: str = kf.path.read_text(encoding="utf-8")
            if type_str in file_text:
                matches.append(kf)

        if len(matches) == 0:
            raise ValueError(f"No file defines type '{type_str}'")
        if len(matches) > 1:
            raise ValueError(
                f"Multiple files define type '{type_str}': {[str(kf.path) for kf in matches]}"
            )

        result[type_str] = matches[0]

    return result
