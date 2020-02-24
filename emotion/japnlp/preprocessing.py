import Mykytea


def tokenize(text: str):
    opt = "-model /usr/local/share/kytea/model.bin"
    mk = Mykytea.Mykytea(opt)
    return [w for w in mk.getWS(text)]


def tokenize_batch(sentences: [str]):
    return [tokenize(exp) for exp in sentences]
