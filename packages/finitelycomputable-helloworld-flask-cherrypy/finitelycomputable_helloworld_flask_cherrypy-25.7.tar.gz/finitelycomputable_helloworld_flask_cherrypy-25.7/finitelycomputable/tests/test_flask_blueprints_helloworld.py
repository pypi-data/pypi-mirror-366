import re
import pytest

from finitelycomputable import flask_blueprints


@pytest.fixture
def client():
        flask_blueprints.application.config['TESTING'] = True

        with flask_blueprints.application.test_client() as client:
            yield client


def test_helloworld(client):
    response = client.get('/hello_world/')
    assert 200 == response.status_code
    assert re.search(b'says "hello, world"\n', response.data)
    assert re.search(b'Flask', response.data)

def test_helloworld_in_env_info(client):
    response = client.get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.helloworld_flask', response.text)
    assert re.search('finitelycomputable.flask_blueprints', response.text)

def test_helloworld_in_index(client):
    response = client.get('/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable-helloworld-flask', response.text)
    assert re.search('finitelycomputable.flask_blueprints', response.text)
