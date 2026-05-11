from pathlib import Path

import pytest


@pytest.fixture
def sample_pack_dir() -> Path:
    """Returns the absolute path to the sample portrait content pack."""
    return Path(__file__).parent / "data" / "sample_pack"
