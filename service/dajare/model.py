# pylint: disable= R0903,R0201,W0613
"""Prediction model used by the service.

Prediction model loads persisted state from the training process and use
model to do the prediction.

"""
import logging
from typing import List
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
        out_kanji = BacktrackSearch(data, input_text).select_solution()
        return Generation(out_kanji)


class BacktrackSearch:
    """Find possible kanjis by backtracking all possibilities
    """
    input_text = ''
    kanas = [[]]
    solutions = []

    def __init__(self, data: List[object], input_text: str):
        """Initialize the prediction."""
        self.kanas = [possible_kanjis for (kana, possible_kanjis) in data]
        self.input_text = input_text
        self.solutions = []

    def select_solution(self) -> str:
        """
        Select a solution which is different from the provided input string.

        :param possible_kanjis: list of possible kanjis for reading
        :param input_text: Japanese input text
        """
        self.__backtrack(0, '')
        return '\n'.join(self.solutions)

    def __backtrack(self, kana_idx: int, current_solution):
        """
        Backtrace-algorithm to find possible dajare-solutions for provided kanas.
        Ignores solution which is equivalent to provided input-string

        :param kana_idx: current kanas for which
        :param current_solution: current possible solution
        :return: All possible kanji solutions for provided kana-string
        """
        if kana_idx == len(self.kanas):
            if current_solution != self.input_text:
                self.solutions.append(current_solution)
            return

        possible_kanjis = self.kanas[kana_idx]
        for nextkanji in possible_kanjis:
            self.__backtrack(kana_idx + 1, current_solution + nextkanji)
