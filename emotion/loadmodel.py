from metaflow import Flow, get_metadata
from emotionflow import EmotionPredictor
import pickle

if __name__ == "__main__":
    run = Flow("EmotionFlow").latest_successful_run
    predictor = run['deliver_model'].task.data.predictor
    pickle.dump(open("emotionpredictor.pkl", "wb"))
