from __future__ import absolute_import

import csv
from operator import itemgetter

from parser.constants import TRIGGER_CHANNEL_LABELS_PATH
from parser.constants import ACTION_CHANNEL_LABELS_PATH
from dialog.utils import levenshtein_distance
from parser.utils import softmax

class KeywordModel(object):
    def __init__(self):
        self.trigger_channels = self._load_channel_names(
            TRIGGER_CHANNEL_LABELS_PATH)
        self.action_channels = self._load_channel_names(
            ACTION_CHANNEL_LABELS_PATH)

    def predict_trigger_channel(self, input, k=1):
        return self._top_k_channel_predictions(self.trigger_channels, input, k)

    def predict_action_channel(self, input, k=1):
        return self._top_k_channel_predictions(self.action_channels, input, k)

    def _top_k_channel_predictions(self, channels, input, k):
        distances = []
        for id_, name in channels.iteritems():
            distance = levenshtein_distance(input, name.lower())
            distances.append(distance)
        softmax_distances = softmax(distances)
        # The smaller the distance, the smaller its softmax value. Therefore,
        # the top predictions correspond to the ones with lowest probabilities.
        # Invert the probabilities to fix this.
        softmax_distances = 1. - softmax_distances

        predictions = []
        for channel, probability in zip(channels, softmax_distances):
            predictions.append((channel, probability))


        top_k_predictions = sorted(predictions, key=itemgetter(1), reverse=True)

        if k != 0:
            top_k_predictions = top_k_predictions[:k]
        return top_k_predictions

    def _load_channel_names(self, csv_file_path):
        channels = {}
        with open(csv_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channels[row['label']] = row['description']
        return channels
