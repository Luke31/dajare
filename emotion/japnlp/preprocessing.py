class Tokenizer:
    def __init__(self, mk):
        self.mk = mk

    def tokenize(self, text: str):
        return [w for w in self.mk.getWS(text)]

    def tokenize_batch(self, sentences: [str]):
        return [self.tokenize(exp) for exp in sentences]
