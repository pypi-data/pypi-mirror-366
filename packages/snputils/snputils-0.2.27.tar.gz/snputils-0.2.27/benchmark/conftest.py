import pytest


def pytest_addoption(parser):
    """
    pytest hook to add custom command line options.
    Must be named pytest_addoption for pytest to recognize it.
    """
    parser.addoption(
        "--memory-profile",
        action="store_true",
        default=False,
        help="Enable memory profiling (slower)"
    )
    parser.addoption(
        "--path",
        action="store",
        help="Path to SNP data"
    )


@pytest.fixture
def path(request):
    """Fixture to get data path"""
    path = request.config.getoption("--path")
    if not path:
        pytest.skip("No path provided")
    return path


@pytest.fixture
def memory_profile(request):
    """Fixture to check if memory profiling is enabled"""
    return request.config.getoption("--memory-profile")
