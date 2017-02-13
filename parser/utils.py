import logging
import numpy as np
import os

from parser.constants import RNN_EXPT_DIRECTORY

def create_experiment_directory(experiment_name):
    try:
        path = RNN_EXPT_DIRECTORY + experiment_name
        logging.info("Creating experiment directories at %s", path)
        os.makedirs(path)
        os.makedirs(path + "/model-checkpoints")
        os.makedirs(path + "/plots")
    except OSError as e:
        logging.error("Error creating directories: %s", e)
        # raise


def verify_experiment_directory(experiment_name):
    path = RNN_EXPT_DIRECTORY + experiment_name
    if not (os.path.exists(path) and os.path.isdir(path)):
        logging.error("Directory %s does not exist.", path)
        raise OSError

def softmax(w, t = 1.0):
    e = np.exp(np.array(w) / t)
    dist = e / np.sum(e)
    return dist
