import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

# Configuration for skipping smoke tests
SKIP_SMOKE = os.getenv("SKIP_SMOKE", "false").lower() == "true"


def get_file_paths():
    """Get list of file paths for each page in the pages folder.

    Returns absolute paths to each file.
    """
    pages_dir = Path(__file__).parent.parent / "src" / "pages"
    file_paths = []

    # Add main app.py
    file_paths.append(str(Path(__file__).parent.parent / "app.py"))

    # Add all Python files in pages directory and its subdirectories
    for file_path in pages_dir.rglob("*.py"):
        file_paths.append(str(file_path))

    return file_paths


def pytest_generate_tests(metafunc):
    """Generate tests for each page in the pages folder.

    https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#pytest-generate-tests

    This generates list of file paths for each page in the pages folder, which will
    automatically be used if a test function has an argument called "file_path".

    Each file path will be the absolute path to each file, but the test ids will be
    just the file name. This is so that the test output is easier to read.

    st_smoke_test.py::test_smoke_page[app.py] PASSED                  [ 33%]
    st_smoke_test.py::test_smoke_page[docs.py] PASSED                             [ 66%]
    st_smoke_test.py::test_smoke_page[pages/agents.py] PASSED                             [100%]
    """
    if "file_path" in metafunc.fixturenames:
        metafunc.parametrize(
            "file_path", get_file_paths(), ids=lambda x: x.split("/")[-1]
        )


@pytest.mark.skipif(SKIP_SMOKE, reason="smoke test is disabled by config")
def test_smoke_page(file_path):
    """Run a basic test on each page in the pages folder.

    This test checks that there are no exceptions raised while the app runs.
    """
    at = AppTest.from_file(file_path, default_timeout=100).run()
    assert not at.exception
