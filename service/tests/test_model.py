# pylint: disable=W0613
"""Just some basic tests for prediction model."""
from dajare.emotionpredictor import EmotionPredictor
from dajare.model import BacktrackSearch, GenerationModel
from unittest.mock import Mock


def test_model_loading():
    """Test model loading based on real_model CLI param."""
    GenerationModel.load_model()

    assert GenerationModel.converter is not None


def test_model_generate():
    """Test calling model prediction method."""
    GenerationModel.generate('ともだち')
    # assert p.output == '友達\n友だち\nトモダチ\n友达'


def test_backtrack_search():
    """Test calling model prediction method."""
    data = [['ともだち', ['友達', '友だち']], ['たべます', ['食べます', '賜べます']]]
    input_text = '友達食べます'
    widx = Mock()
    widx.word2id = {'友達': 0, 'が': 1, '食': 2, 'べます': 3}
    lidx = Mock()
    lidx.label2id = {'嬉しい': 0, '悲しい': 1, '楽しい': 2}
    lidx.id2label = {1: '悲しい', 2: '楽しい', 0: '嬉しい'}

    BacktrackSearch(data, input_text, EmotionPredictor(widx, lidx))\
        .select_solution()
    # assert p == '友達賜べます\n友だち食べます\n友だち賜べます'
