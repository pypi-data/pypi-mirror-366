import re
import pytest

from finitelycomputable import flask_blueprints


@pytest.fixture
def client():
        flask_blueprints.application.config['TESTING'] = True

        with flask_blueprints.application.test_client() as client:
            yield client


def test_env_info(client):
    response = client.get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.flask_blueprints', response.text)
