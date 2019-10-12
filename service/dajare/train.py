"""Script to download the training data and train the model."""

import os
import pickle
import sys
import urllib.request
from typing import Dict

import pandas as pd

import sklearn.pipeline

import dajare.pipeline


class ModelTrainer():
    """Constructor takes a preconfigured Pipeline."""

    def __init__(self, pipeline, target_col, input_features):
        """Constructor."""
        self.pipeline = sklearn.base.clone(pipeline)
        self.target_col = target_col
        self.input_features = input_features
        self.metrics = None

    def train(self, dictjp):
        """Prepare for generation."""
        all_fields = self.input_features + [self.target_col]
        print(all_fields)
        print(dictjp.columns)

    def write_pickled_model(self, outputfilename):
        """Write the pickled model to file."""
        with open(outputfilename, 'wb') as file:
            pickle.dump(self.pipeline, file)

    def write_pickled_trainset(self, outputfilename):
        """Write the training data pickled to disk."""
        self.traindata.to_pickle(outputfilename)

    def write_pickled_validset(self, outputfilename):
        """Write the validation data pickled to disk."""
        self.validdata.to_pickle(outputfilename)


def read_data(url: str, headers: Dict = None) -> pd.DataFrame:
    """Read a CSV form an URL and put it in a pandas Dataframe."""
    if headers is None:
        headers = dict()
    opener = urllib.request.build_opener(
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler()
    )
    urllib.request.install_opener(opener)
    req = urllib.request.Request(url=url, headers=headers)
    with urllib.request.urlopen(req) as file:
        data = pd.read_csv(file)
    return data


def main():
    """Train the model.

    arguments: url outputfilename reqestheaders
    """
    if len(sys.argv) == 6:
        headers = sys.argv[5]
    elif len(sys.argv) == 5:
        headers = dict()
    else:
        os.write(2, b'invalid number of arguments.\n\n'
                    b'usage: train <url> <outputfile>'
                    b' <trainoutfile> <validoutfile>'
                    b' [request-headers]\n')
        sys.exit(-1)
    data = read_data(sys.argv[1], headers)
    data['loan_status'] = data['loan_status'] == 'Fully Paid'
    trainer = ModelTrainer(dajare.pipeline.init_pipeline(),
                           'loan_status',
                           dajare.pipeline.features)
    trainer.train(data)
    trainer.write_pickled_model(sys.argv[2])
    trainer.write_pickled_trainset(sys.argv[3])
    trainer.write_pickled_validset(sys.argv[4])


if __name__ == '__main__':
    main()
