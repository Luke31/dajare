import Mykytea

def tokenize(text):
    opt = "-model /usr/local/share/kytea/model.bin"
    mk = Mykytea.Mykytea(opt)
    return [w for w in mk.getWS(text)]