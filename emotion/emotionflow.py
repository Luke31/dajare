from metaflow import FlowSpec, step, Parameter, conda, conda_base
import sys
import subprocess
from emotionpredictor import EmotionPredictor


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
    
    Example from: https://www.kaggle.com/eray1yildiz/using-lstms-with-attention-for-emotion-recognition
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
        self.labels = self.emotion_map.values()
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

        self.next(self.create_word_index)

    @step
    def create_word_index(self):
        # tokenize each expression and duplicate emotions to both parts.
        # do not assign emotions to tokens that only consist of one kana.
        self.elookup = dict()
        self.max_words = 0  # maximum number of words in a sentence
        word2id = dict()
        label2id = dict()

        # Construction of word2id dict
        for exp, emotion in self.elookup_raw.items():
            for word in mk.getWS(exp):
                if word not in self.kana:
                    self.elookup[word] = set(emotion)
                # Add words to word2id dict if not exist
                if word not in word2id:
                    word2id[word] = len(word2id)
            # If length of the sentence is greater than max_words, update max_words
            if len(exp) > max_words:
                max_words = len(exp)

        # Construction of label2id and id2label dicts
        self.label2id = {l: i for i, l in enumerate(set(self.labels))}
        self.id2label = {v: k for k, v in label2id.items()}
        self.word2id = word2id
        self.label2id = label2id
        self.max_words = max_words

        self.next(self.encode_samples)

    @conda(libraries={'keras': '2.3.1'})
    @step
    def encode_samples(self):
        input_sentences, labels = self.elookup.items()
        # Encode input words and labels
        X = [[self.word2id[word] for word in sentence] for sentence in
             input_sentences]
        Y = [self.label2id[emotion_labels[0]] for emotion_labels in self.labels]

        # Apply Padding to X
        from keras.preprocessing.sequence import pad_sequences
        X = pad_sequences(X, self.max_words)

        # Convert Y to numpy array
        Y = keras.utils.to_categorical(Y, num_classes=len(self.label2id),
                                       dtype='float32')

        # Print shapes
        print("Shape of X: {}".format(X.shape))
        print("Shape of Y: {}".format(Y.shape))
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
        pickle.dump(self.elookup, open('elookup.pkl', 'wb'))
        self.next(self.end)

    @step
    def end(self):
        """
        End-step

        Run 'jupyter-notebook emotionflow-stats.ipynb' to view stats of resulting model
        """
        print("Finished")
        print("Run 'jupyter-notebook emotionflow-stats.ipynb' to view stats of resulting model")


if __name__ == '__main__':
    EmotionFlow()
