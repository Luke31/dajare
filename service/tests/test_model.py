# pylint: disable=W0613
"""Just some basic tests for prediction model."""
from dajare.model import BacktrackSearch, GenerationModel


def test_model_loading():
    """Test model loading based on real_model CLI param."""
    GenerationModel.load_model()

    assert GenerationModel.converter is not None


def test_model_generate():
    """Test calling model prediction method."""
    p = GenerationModel.generate('ともだち')
    assert p.output == '友達\n友だち\nトモダチ\n友达'


def test_backtrack_search():
    """Test calling model prediction method."""
    data = [['ともだち', ['友達', '友だち']], ['たべます', ['食べます', '賜べます']]]
    input_text = '友達食べます'
    p = BacktrackSearch(data, input_text).select_solution()
    assert p == '友達賜べます\n友だち食べます\n友だち賜べます'
