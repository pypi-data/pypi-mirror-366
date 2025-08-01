from falcon import testing
import re
import pytest

from finitelycomputable.falcon_addroute import application


@pytest.fixture
def client():
    return testing.TestClient(application)


def test_helloworld(client):
    response = client.simulate_get('/hello_world/')
    assert 200 == response.status_code
    assert re.search('says "hello, world"\n', response.text)
    assert re.search('Falcon', response.text)

def test_helloworld_in_env_info(client):
    response = client.simulate_get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.helloworld_falcon', response.text)
    assert re.search('finitelycomputable.falcon_addroute', response.text)

def test_helloworld_in_index(client):
    response = client.simulate_get('/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable-helloworld-falcon', response.text)
    assert re.search('finitelycomputable.falcon_addroute', response.text)
