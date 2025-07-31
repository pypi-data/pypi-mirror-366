import typing
import pytest
from pytest import DoctestItem


def pytest_addoption(parser):
    group = parser.getgroup('doctest-only')
    group.addoption(
        '--doctest-only',
        action='store_true',
        help="Only run doctest tests, don't run anything else."
    )

def pytest_collection_modifyitems(session: pytest.Session, config: pytest.Config, items: typing.List[pytest.Item]):
    if config.getoption("--doctest-only"):
        items[:] = [item for item in items if isinstance(item, DoctestItem)]
