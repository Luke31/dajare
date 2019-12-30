"""EmotionPredictor."""
# TODO: Use dependency from emotion/predictor/emotionpredictor!


class EmotionPredictor:
    """EmotionPredictor for prediciton emotion in Japanese sentence."""

    # pylint: disable=too-few-public-methods

    def __init__(self, elookup):
        self.elookup = elookup

    def emotions(self, s: str, mk) -> list((str, set())):
        """
        Predict emotions for a given sentences.

        :param s: sentence of text to analyze e.g. '文句を言ったら怒られた'
        :param mk: Instance of Mykytea tokenizer e.g. mk = Mykytea.Mykytea(opt)
        :return set of emotions for each given sentence as a list
        """
        emotions = set()
        for word in mk.getWS(s):
            if word in self.elookup:
                emotions.update(self.elookup[word])
        return emotions
