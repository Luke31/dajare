# pylint: disable=W0613
"""Just some basic tests for prediction model."""
from dajare.emotionpredictor import EmotionPredictor
from dajare.model import BacktrackSearch, GenerationModel
import pytest  # noqa
from japnlp import Wordindex, Labelsindex
import japnlp
from unittest.mock import Mock


def test_emotionpredictor():
    """Test calling model prediction method."""
    input_text = '友達が食べます'
    widx = Mock()
    widx.word2id = {'友達': 1, 'が': 0, '食': 2, 'べます': 3}

    mk = Mock()
    mk.getWS = lambda x: ['友達', 'が', '食', 'べます']

    ep = EmotionPredictor(widx)
    assert ep.emotions(input_text, mk) == set()
    # assert p == '友達賜べます\n友だち食べます\n友だち賜べます'
