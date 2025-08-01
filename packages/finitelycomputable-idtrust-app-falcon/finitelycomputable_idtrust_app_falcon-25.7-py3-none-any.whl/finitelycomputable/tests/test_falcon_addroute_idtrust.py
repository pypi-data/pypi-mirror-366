from falcon import testing
import re
import pytest

from finitelycomputable.falcon_addroute import application


@pytest.fixture
def client():
    return testing.TestClient(application)

def test_idtrust_in_index(client):
    response = client.simulate_get('/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable-idtrust-app-falcon', response.text)
    assert re.search('finitelycomputable.falcon_addroute', response.text)

def test_idtrust_in_env_info(client):
    response = client.simulate_get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.idtrust_falcon', response.text)
    assert re.search('finitelycomputable.falcon_addroute', response.text)

def test_identification_of_trust_home_blind(client):
    response = client.simulate_get('/identification_of_trust')
    assert 200 == response.status_code
    assert re.search(
        '<button type="submit" name="user_intent" value="Trust">Trust</button>',
        response.text
    )
    assert re.search(
        '<button type="submit" name="user_intent" value="Distrust">Distrust</button>',
        response.text
    )
    assert re.search(
        '<a href="/identification_of_trust/choose_miscommunication">',
        response.text)

def test_identification_of_trust_home_reveal(client):
    response = client.simulate_get(
            '/identification_of_trust/choose_miscommunication')
    assert 200 == response.status_code
    assert re.search(
        '<button type="submit" name="user_intent" value="Trust">Trust</button>',
        response.text
    )
    assert re.search(
        '<button type="submit" name="user_intent" value="Distrust">Distrust</button>',
        response.text
    )
    assert re.search(
        '<input type="range" min="0" max="1" .* name="user_miscommunication"/>',
        response.text
    )
    assert re.search(
        '<input type="range" min="0" max="1" .* name="foil_miscommunication"/>',
        response.text
    )
