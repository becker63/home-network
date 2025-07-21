from pydantic import BaseModel, model_validator
from typing import Optional, List, Callable
from configuration import KFile

class KclTestMetadata(BaseModel):
    kcl_all_files: List[KFile] = []
    kcl_filter_fn: Optional[Callable[[KFile], bool]] = None
    kcl_group_filenames: Optional[List[str]] = None
    kcl_group_filter: Optional[Callable[[KFile], bool]] = None

    @property
    def use_single_file_tests(self) -> bool:
        return callable(self.kcl_filter_fn)

    @property
    def use_named_group_tests(self) -> bool:
        return (
            self.kcl_group_filenames is not None
            and len(self.kcl_group_filenames) > 0
            and callable(self.kcl_group_filter)
        )

    @model_validator(mode='after')
    def validate_filters(self):
        if self.kcl_filter_fn is not None and not callable(self.kcl_filter_fn):
            raise ValueError("kcl_filter_fn must be callable or None")
        if self.kcl_group_filter is not None and not callable(self.kcl_group_filter):
            raise ValueError("kcl_group_filter must be callable or None")
        if self.kcl_group_filenames is not None and not isinstance(self.kcl_group_filenames, list):
            raise ValueError("kcl_group_filenames must be a list or None")
        return self

from pytest import Metafunc
from lib.test_ext.find_kcl_files import find_kcl_files

def pytest_configure(config):
    config._kcl_metadata = KclTestMetadata(kcl_all_files=find_kcl_files())

def pytest_generate_tests(metafunc: Metafunc):
    # Always start with the global file list
    all_files = getattr(metafunc.config, "_kcl_metadata", KclTestMetadata()).kcl_all_files

    # Read metadata *per test function*
    kcl_filter_fn = getattr(metafunc.function, "_kcl_filter_fn", None)
    kcl_group_filenames = getattr(metafunc.function, "_kcl_group_filenames", None)
    kcl_group_filter = getattr(metafunc.function, "_kcl_group_filter", None)

    metadata = KclTestMetadata(
        kcl_all_files=all_files,
        kcl_filter_fn=kcl_filter_fn,
        kcl_group_filenames=kcl_group_filenames,
        kcl_group_filter=kcl_group_filter,
    )

    if metadata.use_single_file_tests and "kf" in metafunc.fixturenames:
        _generate_single_file_tests(metafunc, metadata)
        return

    if metadata.use_named_group_tests:
        _generate_named_group_file_tests(metafunc, metadata)
        return

def _generate_single_file_tests(metafunc: Metafunc, metadata: KclTestMetadata):
    matched = [kf for kf in metadata.kcl_all_files if metadata.kcl_filter_fn(kf)]
    if not matched:
        raise ValueError(f"No KCL files matched for {metafunc.function.__name__}")

    ids = [str(kf.path.relative_to(kf.path.parents[2])) for kf in matched]
    metafunc.parametrize("kf", matched, ids=ids)

def _generate_named_group_file_tests(metafunc: Metafunc, metadata: KclTestMetadata):
    filtered = [kf for kf in metadata.kcl_all_files if metadata.kcl_group_filter(kf)]

    matched = []
    for fname in metadata.kcl_group_filenames:
        match = next((kf for kf in filtered if kf.path.name == fname), None)
        if not match:
            raise ValueError(f"File '{fname}' not found in filtered files for {metafunc.function.__name__}")
        matched.append(match)

    argnames = [
        name for name in metafunc.function.__code__.co_varnames
        if name in metafunc.fixturenames and name != "tmp_path"
    ][:len(matched)]

    if len(argnames) != len(matched):
        raise ValueError(
            f"{metafunc.function.__name__} expects {len(argnames)} args but {len(matched)} files were matched"
        )

    if len(argnames) == 1:
        metafunc.parametrize(
            argnames[0],
            matched,
            ids=[kf.path.name for kf in matched],
        )
    else:
        metafunc.parametrize(
            ",".join(argnames),
            [tuple(matched)],
            ids=[",".join(kf.path.name for kf in matched)],
        )
