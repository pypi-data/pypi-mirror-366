import re
import pytest

from finitelycomputable import flask_dispatcher


@pytest.fixture
def client():
        flask_dispatcher.application.config['TESTING'] = True

        with flask_dispatcher.application.test_client() as client:
            yield client


def test_index(client):
    response = client.get('/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.flask_dispatcher', response.text)

def test_env_info(client):
    response = client.get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.flask_dispatcher', response.text)
