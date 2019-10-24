"""Tests for predict API."""
# pylint: disable=W0621

from flask import url_for
import pytest  # noqa

from dajare import app


@pytest.fixture(scope="module")
def ep_url():
    """Fixture for predict endpoint URL."""
    with app.test_request_context():
        ep = url_for('generate_generate')
    return ep


def test_success_model(client, ep_url):
    """Test that the proper response is given if the parameters are correct."""
    response = client.post(ep_url, data={'input': 'inputtext'})
    assert response.status_code == 200


def test_missing_required_parameter(client, ep_url):
    """Test missing parameter.

    Test that payload with missing parameter will be rejected with the proper
    HTTP reponse code and message.
    """
    missing_param = {}
    response = client.post(ep_url, data=missing_param)
    assert response.status_code == 400
    assert 'Missing input parameter \'input\'' in response.json['output']
