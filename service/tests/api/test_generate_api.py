"""Tests for predict API."""
# pylint: disable=W0621
from unittest.mock import patch

from flask import url_for
import pytest  # noqa

from dajare import app
from dajare.model import Prediction


@pytest.fixture(scope="module")
def ep_url():
    """Fixture for predict endpoint URL."""
    with app.test_request_context():
        ep = url_for('generate_generate')
    return ep


def test_success_model(client, ep_url, real_model):
    """Test that the proper response is given if the parameters are correct."""
    response = client.get(ep_url)
    assert response.status_code == 200


def test_invalid_parameter_type(client, ep_url):
    """Test invalid parameter type.

    Test that invalid parameter type will be rejected with the proper HTTP
    reponse code and message.
    """
    invalid_type = dict(test_payload)
    # Make parameter type bool instead of int
    invalid_type['installment'] = True
    response = client.post(ep_url, data=invalid_type)
    assert response.status_code == 400
    assert 'installment' in response.json['errors']
    assert 'invalid literal for int' in response.json['errors']['installment']


def test_missing_required_parameter(client, ep_url):
    """Test missing parameter.

    Test that payload with missing parameter will be rejected with the proper
    HTTP reponse code and message.
    """
    missing_param = dict(test_payload)
    del missing_param['installment']
    response = client.post(ep_url, data=missing_param)
    assert response.status_code == 400
    assert 'installment' in response.json['errors']
    assert 'Missing required parameter' \
        in response.json['errors']['installment']
