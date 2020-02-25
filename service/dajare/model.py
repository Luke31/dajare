# pylint: disable= R0903,R0201,W0613
"""Prediction model used by the service.

Prediction model loads persisted state from the training process and use
model to do the prediction.

"""
import logging
from typing import List
import pickle
import pykakasi
import requests
import Mykytea

# pylint: disable=import-outside-toplevel
from dajare.emotionpredictor import EmotionPredictor

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
    emotionpredictor = None

    @classmethod
    def load_model(cls):
        """Load model from pickle. Model is kept on the class level."""
        if cls.converter is None or cls.emotionpredictor is None:
            try:
                kakasi = pykakasi.kakasi()
                kakasi.setMode("J", "H")
                # Japanese to ascii, default: no conversion
                cls.converter = kakasi.getConverter()
                # get latest model from metaflow

                with open('wordindex.pkl', 'rb') as f:
                    cls.emotionpredictor = EmotionPredictor(pickle.load(f))
            except FileNotFoundError:
                # Pickled model file doesn't exist during fast testing
                # stage. Dummy model will be used in that case.
                # During real testing stage the test will fail if the model
                # is not loaded.
                logger.warning('Warning: emotionpredictor.pkl not loaded.')

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
        data = resp.json()
        # Check the JSON Response Content documentation below
        out_kanji = BacktrackSearch(data, input_text, cls.emotionpredictor) \
            .select_solution()
        return Generation(out_kanji)


class BacktrackSearch:
    """Find possible kanjis by backtracking all possibilities
    """
    input_text = ''
    kanas = [[]]
    solutions = []
    mk = None

    def __init__(self, data: List[object], input_text: str, emotionpredictor):
        """Initialize the prediction."""
        self.kanas = [possible_kanjis for (kana, possible_kanjis) in data]
        self.input_text = input_text
        self.solutions = []
        self.max_emotion = 0
        opt = "-model /usr/local/share/kytea/model.bin"
        self.mk = Mykytea.Mykytea(opt)
        self.emotionpredictor = emotionpredictor

    def select_solution(self) -> str:
        """
        Select a solution which is different from the provided input string.

        :param possible_kanjis: list of possible kanjis for reading
        :param input_text: Japanese input text
        """
        self.__backtrack(0, '')
        return '\n'.join(solution + ' - (' + '\n'.join(emotions) + ')'
                         for (solution, emotions) in self.solutions)

    def __backtrack(self, kana_idx: int, current_solution):
        """
        Backtrace-algorithm to find possible dajare-solutions for provided kanas.
        Ignores solution which is equivalent to provided input-string
        Chooses solutions with high number of emotions, steadily raising bar

        :param kana_idx: current kanas for which
        :param current_solution: current possible solution
        :return: All possible kanji solutions for provided kana-string
        """
        if kana_idx == len(self.kanas):
            from dajare import app
            if 'FAKE_MODEL' not in app.config:
                emotions = self.emotionpredictor.emotions(current_solution,
                                                          self.mk)
            emotions_cnt = len(emotions)
            if current_solution != self.input_text and \
                    emotions_cnt > self.max_emotion:
                self.solutions.append((current_solution, emotions))
                self.max_emotion = max(self.max_emotion, emotions_cnt)
            return

        possible_kanjis = self.kanas[kana_idx]
        for nextkanji in possible_kanjis:
            self.__backtrack(kana_idx + 1, current_solution + nextkanji)
