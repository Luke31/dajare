"""EmotionPredictor."""
# TODO: Use dependency from emotion/predictor/emotionpredictor!
from japnlp.preprocessing import Tokenizer
from japnlp.index import Wordindex, Labelsindex


class EmotionPredictor:
    """EmotionPredictor for prediciton emotion in Japanese sentence."""

    # pylint: disable=too-few-public-methods

    def __init__(self, wordindex):
        self.wordindex = wordindex

    def emotions(self, s: str, mk) -> {str}:
        """
        Predict emotions for a given sentences.

        :param s: sentence of text to analyze e.g. '文句を言ったら怒られた'
        :param mk: Instance of Mykytea tokenizer e.g. mk = Mykytea.Mykytea(opt)
        :return set of emotions for each given sentence as a list
        """
        emotions = set()

        sentence = Tokenizer(mk).tokenize(s)
        X = [self.wordindex.word2id[word] for word in sentence if word
             in self.wordindex.word2id]

        # Call model REST

        return emotions
