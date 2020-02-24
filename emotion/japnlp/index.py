

class Wordindex:
    def __init__(self, sentences: [[str]]):
        # Initialize word2id and label2id dictionaries that will be used to encode words and labels
        self.word2id = dict()

        self.max_words = 0  # maximum number of words in a sentence

        # Construction of word2id dict
        for sentence in sentences:
            for word in sentence:
                # Add words to word2id dict if not exist
                if word not in self.word2id:
                    self.word2id[word] = len(self.word2id)
            # If length of the sentence is greater than max_words, update max_words
            if len(sentence) > self.max_words:
                self.max_words = len(sentence)


class Labelsindex:
    def __init__(self, labels: [str]):
        self.label2id = dict()
        self.id2label = dict()

        # Construction of label2id and id2label dicts
        label2id = {l: i for i, l in enumerate(sorted(set(labels)))}
        id2label = {v: k for k, v in label2id.items()}

        self.label2id = label2id
        self.id2label = id2label
