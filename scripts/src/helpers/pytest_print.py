# helpers/pytest_print.py

from pytest_print import PrettyPrinter, PrettyPrinterFactory, Formatter
import pytest


@pytest.fixture(scope="session")
def pretty(create_pretty_printer: PrettyPrinterFactory) -> PrettyPrinter:
    formatter = Formatter(
        indentation="  ",
        head=" ",
        space=" ",
        icon="⏩",
        timer_fmt="[{elapsed:.20f}]"
    )
    return create_pretty_printer(formatter=formatter)
