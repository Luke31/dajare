from metaflow import FlowSpec, step, Parameter, conda, conda_base
import os
import sys
import subprocess

def get_python_version():
    import platform
    versions = {'3' : '3.7.5'}
    return versions[platform.python_version_tuple()[0]]


@conda_base(python=get_python_version())
class EmotionFlow(FlowSpec):
    """
    A flow to assess various models for emotion detection in Japanese text
    """
    @step
    def start(self):
        print("EmotionFlow is starting...")
        self.next(self.load)

    @conda(libraries={'pandas' : '0.25.3'})
    @step
    def load(self):
        import pandas as pd
        self.ecorp = pd.read_csv('data/D18-2018.7.24.csv')
        print(self.ecorp)
        self.available_emotions = pd.read_csv('data/emotion_assignment.csv')
        print(self.available_emotions)
        self.next(self.prepare_lookup)

    @conda(libraries={'pandas' : '0.25.3'})
    @step
    def prepare_lookup(self):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kytea==0.1.4"])
        #prepare tokenizer
        import Mykytea
        opt = "-model /usr/local/share/kytea/model.bin"
        mk = Mykytea.Mykytea(opt)
        # hiragana, katakana and unionedkanas
        hira = {chr(l) for l in range(12353,12439)}
        kata = {chr(l) for l in range(12449,12539)}
        kana = hira.union(kata)
        
        #prepare emotion-map
        self.emotion_map = {row['Symbol']: row['Emotion'] for index, row in self.available_emotions.iterrows()}
        self.emotion_map.update({'面':''})
        self.emotion_map.items()

        #prepare raw-lookup
        self.elookup_raw = {row['Word']: [self.emotion_map[emotion]
                         for emotion in list(row['Emotion'])] for index, row in self.ecorp.iterrows()}

        #tokenize and stemming
        self.elookup = dict()
        for exp, emotion in self.elookup_raw.items():
            for word in mk.getWS(exp):
                if word not in kana:
                    self.elookup[word] = set(emotion)
        self.next(self.deliver_model)

    @step
    def deliver_model(self):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kytea==0.1.4"])
        import pickle

        class EmotionPredictor(object):
            def __init__(self, elookup):
                import Mykytea
                opt = "-model /usr/local/share/kytea/model.bin"
                self.mk = Mykytea.Mykytea(opt)
                self.elookup = elookup

            # emotion lookup
            def emotions(s):
                emotions = set()
                for word in self.mk.getWS(s):
                    if word in self.elookup:
                         emotions.update(self.elookup[word])
                return emotions
        
        predictor = EmotionPredictor(self.elookup)
        pickle.dump(predictor, open('file.pkl', 'wb'))
        self.next(self.end)

    @step
    def end(self):
        """
        End-step
        """
        print("")

class EmotionPredictor():
    def __init__(self, elookup):
        import Mykytea
        opt = "-model /usr/local/share/kytea/model.bin"
        self.mk = Mykytea.Mykytea(opt)
        self.elookup = elookup

        # emotion lookup
    def emotions(s):
        emotions = set()
        for word in self.mk.getWS(s):
            if word in self.elookup:
                 emotions.update(self.elookup[word])
        return emotions


if __name__ == '__main__':
    EmotionFlow()
