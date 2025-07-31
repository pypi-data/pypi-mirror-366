import os
from unittest.mock import patch

import pytest

from .fixtures.simple_app import *
from .fixtures.sse_server import *


class MockContext:
    class RequestContext:
        class LifespanContext:
            def __init__(self):
                self.session_id = "test-session"

        def __init__(self):
            self.lifespan_context = self.LifespanContext()

    def __init__(self):
        self.request_context = self.RequestContext()


@pytest.fixture
def mock_context():
    return MockContext()


@pytest.fixture
def simulation_env():
    with patch.dict(
        os.environ,
        {
            "VERIS_MOCK_ENDPOINT_URL": "http://test-endpoint",
            "ENV": "simulation",
        },
    ):
        yield


@pytest.fixture
def production_env():
    with patch.dict(
        os.environ,
        {
            "VERIS_MOCK_ENDPOINT_URL": "http://test-endpoint",
            "ENV": "production",
        },
    ):
        yield
