# pylint: disable= R0903,R0201,W0613
"""Prediction model used by the service.

Prediction model loads persisted state from the training process and use
model to do the prediction.

"""
import logging
import pykakasi
import requests

logger = logging.getLogger(__name__)


class Generation:
    """Generation class used to pass an answer from generation model."""

    def __init__(self, output='DajareNai'):
        """Initialize the prediction."""
        self.output = output


class GenerationModel:
    """Prediction model used by the service.

    Prediction model loads persisted state from the training process and use
    model to do the prediction.
    """

    converter = None

    @classmethod
    def load_model(cls):
        """Load model from pickle. Model is kept on the class level."""
        if cls.converter is None:
            try:
                kakasi = pykakasi.kakasi()
                kakasi.setMode("J", "H")  # Japanese to ascii, default: no conversion
                cls.converter = kakasi.getConverter()

                # with open('model.pkl', 'rb') as f:
                #    cls.pipeline = pickle.load(f)
            except FileNotFoundError:
                # Pickled model file doesn't exist during fast testing
                # stage. Dummy model will be used in that case.
                # During real testing stage the test will fail if the model
                # is not loaded.
                logger.warning('Warning: model.pkl not loaded.')

    @classmethod
    def generate(cls, input_text):
        """Return generation based on the input arguments.

        :param input_text: The input data arguments.
        :type input_text: str

        :return: the Prediction object.
        :rtype: Prediction
        """
        cls.load_model()
        in_kanji = input_text
        print(f'Input-Kanji: {in_kanji}')
        in_kana = cls.converter.do(in_kanji)
        print(f'Input-Kana: {in_kana}')
        url = f'http://www.google.com/transliterate?langpair=ja-Hira|ja&text={in_kana}'

        resp = requests.get(url=url)
        data = resp.json()  # Check the JSON Response Content documentation below

        out_kanji = ''.join([possible_kanjis[0] for (kana, possible_kanjis) in data])
        print(f'Out-Kanji: {out_kanji}')

        return Generation(out_kanji)
