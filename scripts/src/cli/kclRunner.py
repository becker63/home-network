import sys
import pytest
from helpers import find_project_root

def main():
    # Default to only running validation tests
    markers = sys.argv[1:] if len(sys.argv) > 1 else ["-m", "not automation"]

    # Ensure all args passed to pytest are strings
    test_dir = str(find_project_root() / "kcl")

    # Call pytest with desired options
    exit_code = pytest.main([
        "-q",        # quiet output
        *markers,    # include any CLI overrides
        test_dir,    # path to collected test files
    ])

    sys.exit(exit_code)
