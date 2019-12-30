"""Load lookup-array from metaflow.

Currently not in use, as you need to configure metaflow also in docker.
"""

import pickle

from metaflow import Flow

if __name__ == "__main__":
    run = Flow("EmotionFlow").latest_successful_run
    predictor = run['deliver_model'].task.data.predictor
    pickle.dump(open("elookup.pkl", "wb"))
