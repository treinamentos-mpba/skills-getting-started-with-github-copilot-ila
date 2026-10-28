import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Mutate in place: app.py holds a reference to this same dict.
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)
