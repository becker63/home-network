import pytest
from pytest import Metafunc
from lib.test_ext.find_kcl_files import find_kcl_files

def pytest_configure(config):
    config._kcl_all_files = find_kcl_files()

def pytest_generate_tests(metafunc: Metafunc):
    config_files = getattr(metafunc.config, "_kcl_all_files", [])

    if "kf" in metafunc.fixturenames:
        _generate_single_file_tests(metafunc, config_files)
        return

    if getattr(metafunc.function, "_kcl_group_filenames", None):
        _generate_named_group_file_tests(metafunc, config_files)
        return

def _generate_single_file_tests(metafunc: Metafunc, config_files):
    filter_fn = getattr(metafunc.function, "_kcl_filter_fn", None)
    if not callable(filter_fn):
        return

    matched = [kf for kf in config_files if filter_fn(kf)]
    if not matched:
        raise ValueError(f"No KCL files matched for {metafunc.function.__name__}")

    ids = [str(kf.path.relative_to(kf.path.parents[2])) for kf in matched]
    metafunc.parametrize("kf", matched, ids=ids)

def _generate_named_group_file_tests(metafunc: Metafunc, config_files):
    filenames = getattr(metafunc.function, "_kcl_group_filenames", None)
    filter_fn = getattr(metafunc.function, "_kcl_group_filter", None)

    if not filenames or not callable(filter_fn):
        return

    filtered = [kf for kf in config_files if filter_fn(kf)]

    matched = []
    for fname in filenames:
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
        # Single argument: pass list of KFile objects directly
        metafunc.parametrize(
            argnames[0],
            matched,
            ids=[kf.path.name for kf in matched],
        )
    else:
        # Multiple arguments: pass tuples of matched files
        metafunc.parametrize(
            ",".join(argnames),
            [tuple(matched)],
            ids=[",".join(kf.path.name for kf in matched)],
        )
