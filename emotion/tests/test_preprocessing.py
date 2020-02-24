# pylint: disable=W0621
"""pytest configuration. E.g. fixtures for all tests."""

import logging
import time
from multiprocessing import Process
from japnlp import preprocessing

import pytest


def test_tokenizer():
    """Create an instance of Flask server."""
    input = '友達と話す'
    out = preprocessing.tokenize(input)
    assert out == ['友達', 'と', '話す']
