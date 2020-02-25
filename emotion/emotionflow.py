from metaflow import FlowSpec, step, current, Parameter, conda, conda_base
import sys
import subprocess
import os
from japnlp.preprocessing import Tokenizer
from japnlp.index import Wordindex, Labelsindex


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
        self.emotion_map.update({'面': ''})
        self.emotion_map.items()
        self.next(self.prepare_tokens)

    @step 
    def prepare_kana_set(self):
        """
        Prepeare set for unioned kanas(Hiragana, Katanakana)
        """
        hira = {chr(l) for l in range(12353,12439)}
        kata = {chr(l) for l in range(12449,12539)}
        self.kana = hira.union(kata)
        self.next(self.prepare_tokens)

    @conda(libraries={'pandas': '0.25.3'})
    @step
    def prepare_tokens(self, inputs):
        """
        Tokenization of input_sentences and target labels
        """
        self.merge_artifacts(inputs)
        
        # prepare Japanese tokenizer
        import Mykytea
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kytea==0.1.4"])
        opt = "-model /usr/local/share/kytea/model.bin"
        mk = Mykytea.Mykytea(opt)
        self.input_sentences = Tokenizer(mk).tokenize_batch(self.ecorp['Word'].values.tolist())
        self.labels = [self.emotion_map[emotions[:1]] for emotions in self.ecorp['Emotion'].values.tolist()]

        self.next(self.create_word_labels_index)

    @step
    def create_word_labels_index(self):
        """
        Creating Vocabulary (word and labels index)
        :return:
        """

        # Wordindex
        self.wordindex = Wordindex(self.input_sentences)
        self.labelsindex = Labelsindex(self.labels)

        self.next(self.encode_samples)

    @conda(libraries={'tensorflow': '2.1.0'})
    @step
    def encode_samples(self):
        """
        Encoding samples with corresponing integer values
        :return:
        """
        import tensorflow as tf

        # Encode input words and labels
        X = [[self.wordindex.word2id[word] for word in sentence] for sentence in
             self.input_sentences]
        Y = [self.labelsindex.label2id[label] for label in self.labels]

        # Apply Padding to X
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        X = pad_sequences(X, self.wordindex.max_words)

        # Convert Y to numpy array
        Y = tf.keras.utils.to_categorical(Y, num_classes=len(self.labelsindex.label2id),
                                       dtype='float32')

        # Print shapes
        print("Shape of X: {}".format(X.shape))
        print("Shape of Y: {}".format(Y.shape))
        self.X = X
        self.Y = Y
        self.next(self.build_lstm)

    @conda(libraries={'tensorflow': '2.1.0'})
    @step
    def build_lstm(self):
        """
        Build LSTM model with attention
        :return:
        """
        import tensorflow as tf

        embedding_dim = 100  # The dimension of word embeddings

        # Define input tensor
        sequence_input = tf.keras.Input(shape=(self.wordindex.max_words,), dtype='int32')

        # Word embedding layer
        embedded_inputs = tf.keras.layers.Embedding(len(self.wordindex.word2id) + 1,
                                                 embedding_dim,
                                                 input_length=self.wordindex.max_words)(
            sequence_input)

        # Apply dropout to prevent overfitting
        embedded_inputs = tf.keras.layers.Dropout(0.2)(embedded_inputs)

        # Apply Bidirectional LSTM over embedded inputs
        lstm_outs = tf.keras.layers.Bidirectional(
            tf.keras.layers.LSTM(embedding_dim, return_sequences=True)
        )(embedded_inputs)

        # Apply dropout to LSTM outputs to prevent overfitting
        lstm_outs = tf.keras.layers.Dropout(0.2)(lstm_outs)

        # Attention Mechanism - Generate attention vectors
        input_dim = int(lstm_outs.shape[2])
        permuted_inputs = tf.keras.layers.Permute((2, 1))(lstm_outs)
        attention_vector = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(1))(
            lstm_outs)
        attention_vector = tf.keras.layers.Reshape((self.wordindex.max_words,))(attention_vector)
        attention_vector = tf.keras.layers.Activation('softmax',
                                                   name='attention_vec')(
            attention_vector)
        attention_output = tf.keras.layers.Dot(axes=1)(
            [lstm_outs, attention_vector])

        # Last layer: fully connected with softmax activation
        fc = tf.keras.layers.Dense(embedding_dim, activation='relu')(
            attention_output)
        output = tf.keras.layers.Dense(len(self.labelsindex.label2id), activation='softmax')(fc)

        # Finally building model
        model = tf.keras.Model(inputs=[sequence_input], outputs=output)
        model.compile(loss="categorical_crossentropy", metrics=["accuracy"],
                      optimizer='adam')

        # Print model summary
        model.summary()

        # Train model 10 iterations
        model.fit(self.X, self.Y, epochs=2, batch_size=64, validation_split=0.1, shuffle=True)

        # Re-create the model to get attention vectors as well as label prediction
        model_with_attentions = tf.keras.Model(inputs=model.input,
                                            outputs=[model.output,
                                                     model.get_layer(
                                                         'attention_vec').output])

        # Save model in SavedModel format for Tensorflow Serving.
        export_path = f'../models/{current.flow_name}/{current.run_id}/'
        os.makedirs(export_path)

        model.save(export_path, save_format='tf')
        self.next(self.exportindex)

    @step
    def exportindex(self):
        import pickle

        pickle.dump(self.wordindex, open('wordindex.pkl', 'wb'))
        pickle.dump(self.labelsindex, open('labelsindex.pkl', 'wb'))
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
