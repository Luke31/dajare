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
    model_name = Parameter('model_name',
                        help='Pickle filename for EmotionPredictor object',
                        default='emotionpredictor.pkl')

    """
    Model for emotion detection in Japanese text
    """
    @step
    def start(self):
        """
        Start-step
        """
        print("EmotionFlow is starting...")
        self.next(self.load)

    @conda(libraries={'pandas' : '0.25.3'})
    @step
    def load(self):
        """
        Load emotion corpus with expressions and multiple assigned emotions per expression. 
        """
        import pandas as pd
        self.ecorp = pd.read_csv('data/D18-2018.7.24.csv')
        print(self.ecorp)
        self.available_emotions = pd.read_csv('data/emotion_assignment.csv')
        print(self.available_emotions)
        self.next(self.prepare_emotion_dict, self.prepare_kana_set)

    @conda(libraries={'pandas' : '0.25.3'})
    @step
    def prepare_emotion_dict(self):
        """
        Prepare dictionary to map short form of emotion to more understandable longer form of emtion:
        悲 -> 悲しさ or 恐 -> 恐れ（恐縮等の意味で）
        """
        self.emotion_map = {row['Symbol']: row['Emotion'] for index, row in self.available_emotions.iterrows()}
        self.emotion_map.update({'面':''})
        self.emotion_map.items()
        self.next(self.prepare_lookup)

    @step 
    def prepare_kana_set(self):
        """
        Prepeare set for unioned kanas(Hiragana, Katanakana)
        """
        hira = {chr(l) for l in range(12353,12439)}
        kata = {chr(l) for l in range(12449,12539)}
        self.kana = hira.union(kata)
        self.next(self.prepare_lookup)

    @conda(libraries={'pandas' : '0.25.3'})
    @step
    def prepare_lookup(self, inputs):
        """
        Prepare tokenized dictionary for emotions lookup.

        One expression may have multiple emotions assigned.
        For each token of expression assign all expression emotions.
        """
        self.merge_artifacts(inputs)
        
        # prepare Japanese tokenizer
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kytea==0.1.4"])
        import Mykytea
        opt = "-model /usr/local/share/kytea/model.bin"
        mk = Mykytea.Mykytea(opt)
        
        # prepare list of emotions per expression
        self.elookup_raw = {row['Word']: [self.emotion_map[emotion]
                         for emotion in list(row['Emotion'])] for index, row in self.ecorp.iterrows()}

        # tokenize each expression and duplicate emotions to both parts. 
        # do not assign emotions to tokens that only consist of one kana.
        self.elookup = dict()
        for exp, emotion in self.elookup_raw.items():
            for word in mk.getWS(exp):
                if word not in self.kana:
                    self.elookup[word] = set(emotion)
        self.next(self.deliver_model)

    @step
    def deliver_model(self):
        """
        Initialize Japanese EmotionPredictor model and save in flow under 'self.predictor'.
        User Predcitor as follows: predictor.emotions('文句を言ったら怒られた')

        Additionally saved as local pickle-file according to model_name-param
        """
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kytea==0.1.4"])
        import pickle

        self.predictor = EmotionPredictor(self.elookup)
        pickle.dump(self.predictor, open(self.model_name, 'wb'))
        self.next(self.end)

    @step
    def end(self):
        """
        End-step

        Run 'jupyter-notebook emotionflow-stats.ipynb' to view stats of resulting model
        """
        print("Finished")
        print("Run 'jupyter-notebook emotionflow-stats.ipynb' to view stats of resulting model")

class EmotionPredictor():
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


if __name__ == '__main__':
    EmotionFlow()
