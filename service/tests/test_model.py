# pylint: disable=W0613
"""Just some basic tests for prediction model."""
from dajare.model import GenerationModel


def test_model_loading(real_model):
    """Test model loading based on real_model CLI param."""
    GenerationModel.load_model()

    assert GenerationModel.converter is not None


def test_model_generate(fake_model):
    """Test calling model prediction method."""
    p = GenerationModel.predict('ともだち')
    assert p.output == '友達'
