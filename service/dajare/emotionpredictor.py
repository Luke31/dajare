"""EmotionPredictor."""
# TODO: Use dependency from emotion/predictor/emotionpredictor!
from japnlp.preprocessing import Tokenizer
from japnlp.index import Wordindex, Labelsindex
import requests
import json
import logging

logger = logging.getLogger(__name__)

class EmotionPredictor:
    """EmotionPredictor for prediciton emotion in Japanese sentence."""

    # pylint: disable=too-few-public-methods

    def __init__(self, wordindex: Wordindex, labelsindex: Labelsindex):
        self.wordindex = wordindex
        self.labelsindex = labelsindex

    def emotions(self, s: str, mk) -> {str}:
        """
        Predict emotions for a given sentences.

        :param s: sentence of text to analyze e.g. '文句を言ったら怒られた'
        :param mk: Instance of Mykytea tokenizer e.g. mk = Mykytea.Mykytea(opt)
        :return set of emotions for given sentence as a list
        """
        emotions = set()

        sentence = Tokenizer(mk).tokenize(s)
        X = [self.wordindex.word2id[word] for word in sentence if word
             in self.wordindex.word2id]

        # Apply Padding to X
        # from tensorflow.keras.preprocessing.sequence import pad_sequences
        # X = pad_sequences(X, self.wordindex.max_words)
        # assert len(X) == self.wordindex.max_words

        # Call model REST
        payload = {
            "instances": [{'input_1': X}]
        }
        # sending post request to TensorFlow Serving server
        r = requests.post(
            'http://localhost:8038/v1/models/EmotionFlow:predict',
            json=payload)
        content = json.loads(r.content.decode('utf-8'))
        try:
            label_probs = content['predictions']
            # Decode predictions decode_predictions
            label_probs_labeled = {self.labelsindex.id2label[_id]: prob for
                                   (label, _id),
                                   prob in
                                   zip(self.labelsindex.label2id.items(),
                                       label_probs[0])}
        except KeyError:
            logger.error('Error when calling backend model.', content)
            label_probs_labeled = content

        return label_probs_labeled
