# pylint: disable=W0621
"""pytest configuration. E.g. fixtures for all tests."""

import logging
import time
from multiprocessing import Process
from japnlp import preprocessing

import pytest


def test_tokenizer():
    inp = '友達と話す'
    out = preprocessing.tokenize(inp)
    assert out == ['友達', 'と', '話', 'す']

def test_tokenizer_batch():
    inp = ['友達と話す', '私の話']
    out = preprocessing.tokenize_batch(inp)
    assert out == [['友達', 'と', '話', 'す'], ['私', 'の', '話']]
