from falcon import testing
import re
import pytest

from finitelycomputable.falcon_addroute import application


@pytest.fixture
def client():
    return testing.TestClient(application)


def test_index(client):
    response = client.simulate_get('/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.falcon_addroute', response.text)

def test_env_info(client):
    response = client.simulate_get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.falcon_addroute', response.text)
