from typing import Any, TypeAlias, List, Dict
from pathlib import Path
import pytest

from configuration import FILTERS, ProjectFilters, KFile
from lib.debug import debug_print

TestCase: TypeAlias = Any  # pytest.param(...)


def filter_kcl_files(
    all_files: list[KFile],
    *filters: ProjectFilters,
) -> list[TestCase]:
    seen_paths: set[Path] = set()
    cases: list[TestCase] = []

    for pf in filters:
        filter_fn = FILTERS[pf]
        debug_print(f"\n[DEBUG] Applying filter: {pf.name}")
        matched_this_filter = False

        for kf in all_files:
            if not filter_fn(kf):
                continue
            if kf.path in seen_paths:
                continue

            matched_this_filter = True
            seen_paths.add(kf.path)
            debug_print(f"[DEBUG]  ✓ Matched: {kf.path}")
            cases.append(pytest.param(pf, kf, id=f"{pf.value}::{kf.path.stem}"))

        if not matched_this_filter:
            debug_print(f"[DEBUG]  ⚠️ No matches found for filter: {pf.name}")

    return cases


def find_unique_kfiles_by_types(type_strs: List[str], all_kfiles: List[KFile]) -> Dict[str, KFile]:
    result: Dict[str, KFile] = {}

    for type_str in type_strs:
        debug_print(f"\n[DEBUG] Searching for type: '{type_str}'")
        matches: List[KFile] = []

        for kf in all_kfiles:
            file_text: str = kf.path.read_text(encoding="utf-8")
            if type_str in file_text:
                debug_print(f"[DEBUG]  ✓ Found '{type_str}' in: {kf.path}")
                matches.append(kf)

        if len(matches) == 0:
            debug_print(f"[DEBUG]  ❌ No match found for type '{type_str}'")
            raise ValueError(f"No file defines type '{type_str}'")
        if len(matches) > 1:
            debug_print(f"[DEBUG]  ❌ Multiple matches for type '{type_str}':")
            for match in matches:
                debug_print(f"[DEBUG]     - {match.path}")
            raise ValueError(
                f"Multiple files define type '{type_str}': {[str(kf.path) for kf in matches]}"
            )

        result[type_str] = matches[0]

    return result
