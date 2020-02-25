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

    lidx = Mock()
    lidx.label2id = {'嬉しい': 0, '悲しい': 1, '楽しい': 2}
    lidx.id2label = {1: '悲しい', 2: '楽しい', 0: '嬉しい'}

    mk = Mock()
    mk.getWS = lambda x: ['友達', 'が', '食', 'べます', '食', '食', '食', '食', '食']

    ep = EmotionPredictor(widx, lidx)
    emotions = ep.emotions(input_text, mk)
    assert '嬉しい' in emotions
    assert '悲しい' in emotions
    assert '楽しい' in emotions
