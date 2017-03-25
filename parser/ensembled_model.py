import logging
import numpy as np


class EnsembledModel(object):
    """Ensemble of multiple models."""

    def __init__(self):
        self._models = []
        """`list` of `model.Model`: List of models to be ensembled."""

    def add_model(self, model):
        """Adds model to the list of models to be ensembled.

        Args:
            model (`model.Model`): Model to be added.
        """
        self._models.append(model)

    def test_data(self):
        """Returns the test data loaded in the models constituting the ensemble

        Returns:
            `numpy.ndarray`, `numpy.ndarray`, `numpy.ndarray`: The test inputs,
            their true labels, and their sequence lengths.
        """
        try:
            return self._models[0].x_test, self._models[0].y_test, \
                   self._models[0].seq_lens_test
        except IndexError:
            return None, None, None

    def predict(self, input, k=1):
        """Calculates top-`k` predictions for the supplied `input`.

        The top-`k` predictions are obtained by ensembling the predictions of
        all the models. Simple averaging of softmax-predictions is used for
        ensembling.

        `k` = 0 returns a sorted list of all predictions.

        Args:
            input (str): Description of recipe.
            k (int, optional): Number of top predictions to be returned.
            Defaults to 1.

        Returns:
            `list` of (`str`,`float`): Sorted list of top-`k` predictions for
            the given description, along with the assigned probabilities.
            Predictions are in the form of labels represented by strings
            (such as "new_photo_post" for a Trigger Function).
        """
        prediction = self._averaged_predictions(np.array([input]),
                                                preprocess=True).reshape((-1,))
        logging.debug("Averaged prediction %s", prediction)

        ids = np.argpartition(prediction, -k)[-k:]
        # Ids of top-k labels.
        top_k_indices = ids[np.argsort(prediction[ids])][::-1]
        logging.debug("Top k=%s labels' ids %s", k, top_k_indices)

        # Convert label-ids to readable label-strings using
        # `Model.label_reverse_map`.
        labels_reverse_map = self._models[0].labels_reverse_map
        top_k_predictions = []
        for idx in top_k_indices:
            tup = (labels_reverse_map[idx], prediction[idx])
            top_k_predictions.append(tup)
        return top_k_predictions

    def evaluate(self):
        """Evaluates the ensemble of models on the test set.

        The test set used is the one loaded in the first model. It is assumed
        that all models are loaded with the same subset of the full test set.
        """
        logging.debug("Starting evaluation of ensembled model on test data.")

        inputs = self._models[0].x_test
        labels = self._models[0].y_test
        seq_lens = self._models[0].seq_lens_test
        mistakes = self.prediction_mistakes(inputs, labels, seq_lens)
        error = np.mean(mistakes)
        logging.info("Test Error = %s", error)

    def prediction_mistakes(self, inputs, labels, seq_lens):
        """Computes averaged predictions of the models and returns identifies
        the instances where the model makes a mistake.

        Args:
            inputs (`numpy.ndarray`): List of input descriptions in tokenized
                form, i.e., as a 2D numpy array of tokens
            labels (`numpy.ndarray`): True labels in the form of a 2D numpy
                array. Each row is a one-hot vector for the label.
            seq_lens (`list` of `int`, optional): The list of lengths of
                descriptions as returned by
                `dataset.Dataset.description_lengths_before_padding`.

        Returns:
            numpy.ndarray: An array containing `True` and `False`, `True`
            representing correct prediction by the model for that input.
        """
        averaged_predictions = self._averaged_predictions(inputs, seq_lens,
                                                          preprocess=False)
        # Calculate classification error.
        p = np.argmax(averaged_predictions, axis=1)
        l = np.argmax(labels, axis=1)
        mistakes = np.not_equal(p, l)
        return mistakes

    def prediction_confidences(self, inputs, labels, seq_lens):
        """Computes averaged predictions of the models and returns confidences
        of top prediction for each input in `inputs`

        Args:
            inputs (`numpy.ndarray`): List of input descriptions in tokenized
                form, i.e., as a 2D numpy array of tokens
            labels (`numpy.ndarray`): True labels in the form of a 2D numpy
                array. Each row is a one-hot vector for the label.
            seq_lens (`list` of `int`, optional): The list of lengths of
                descriptions as returned by
                `dataset.Dataset.description_lengths_before_padding`.

        Returns:
            numpy.ndarray: An array containing confidence of top prediction for
            each input in `inputs`.
        """
        averaged_predictions = self._averaged_predictions(inputs, seq_lens,
                                                          preprocess=False)
        return np.max(averaged_predictions, axis=1)

    def _averaged_predictions(self, inputs, seq_lens=None, preprocess=True):
        """Computes average of softmax-prediction output of all the models.

        Each model is supplied with provided `inputs`, optionally we a request
        to pre-process the `inputs`. The models softmax output is then used.

        Args:
            inputs (`list` of `str` or `numpy.ndarray`): List of input
                descriptions. The descriptions can either be tokenized -- as a
                2D numpy array of tokens -- in which case `preprocess` should be
                `False` or raw strings of texts -- `list` of `str` -- in which
                case `preprocess` should be `True`.
            seq_lens (`list` of `int`, optional): The list of lengths of
                descriptions as returned by
                `dataset.Dataset.description_lengths_before_padding`. This is
                required if `preprocess` is `False`. Defaults to `None`, which
                works with `preprocess` set to True.
            preprocess (bool, optional): Set to `True` if the `inputs` needs to
                be pre-processed. Defaults to `True`.

        Returns:
            numpy.ndarray: Mean of softmax outputs of all the models of shape
            (num_inputs, num_classes)
        """
        predictions = []
        for model in self._models:
            preds = model.predictions(inputs, seq_lens, preprocess)
            predictions.append(preds)

        averaged_predictions = np.mean(predictions, axis=0)
        return averaged_predictions
