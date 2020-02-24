# pylint: disable=W0621
"""pytest configuration. E.g. fixtures for all tests."""

import logging
import time
from multiprocessing import Process
from japnlp import preprocessing

from japnlp.index import Wordindex, Labelsindex

import pytest


def test_prepare_words():
    inp = [['友達', 'と'], ['私', 'と', '話']]
    idx = Wordindex(inp)
    assert idx.max_words == 3
    assert idx.word2id == {'友達': 0, 'と': 1, '私': 2, '話': 3}

def test_labels_index():
    inp = ['嬉しい', '楽しい','悲しい']
    idx = Labelsindex(inp)
    assert idx.label2id == {'嬉しい': 0, '悲しい': 1, '楽しい': 2}
    assert idx.id2label == {1: '悲しい', 2: '楽しい', 0: '嬉しい'}
