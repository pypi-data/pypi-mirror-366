import os

import pytest


@pytest.fixture(autouse=True)
def skip_if_no_private_key(request):
    """Skip tests that require private key when it's not available."""
    if request.node.get_closest_marker("requires_private_key") and not os.getenv("PRIVATE_KEY"):
        pytest.skip("Test requires PRIVATE_KEY environment variable")
