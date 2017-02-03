import csv
import logging

import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import tensorflow as tf

from constants import EVALUATION_FREQ, STOP_FILE, VOCAB_FILE
from dataset import Dataset
from rnn import LatentAttentionNetwork
from utils import softmax


class Model(object):
    """Model class that exposes methods to load dataset, train and checkpoint
    a model, restore model, evaluate model, and expose methods to get online
    predictions from a model.

    Attributes:
        labels_map (dict): Maps `str` label keywords to `int` ids.
        labels_reverse_map (dict): Maps `int` ids to corresponding `str` labels.
        config: A configuration class, similar to `configs.PaperConfigurations`.
        network (`rnn.RNN`): The recurrent neural network underlying the model;
            an instance of RNN class.
        path (str): Root directory containing dataset.
        stem (bool): Set to True if the input descriptions should be stemmed.
        x_train (numpy.ndarray): Input recipes' descriptions from the train set.
            Each row is description in the form of a list of token ids.
        x_validate (numpy.ndarray): Input recipes' descriptions from validate
            set. Each row is description in the form of a list of token ids.
        x_test (numpy.ndarray): Input recipes' descriptions from the test set.
            Each row is description in the form of a list of token ids.
        y_train (numpy.ndarray): Recipes' labels from the train set. Each row is
            a one-hot vector representing the label for the corresponding
            recipe.
        y_validate (numpy.ndarray): Recipes' labels from the validate set. Each
            row is a one-hot vector representing the label for the corresponding
            recipe.
        y_test (numpy.ndarray): Recipes' labels from the test set. Each row is
            a one-hot vector representing the label for the corresponding
            recipe.
        seq_lens_train (numpy.ndarray): Each row represents the lengths of
            descriptions of a recipe in the train set. The lengths are those
            that are returned by `dataset.Dataset.load_train` method.
        seq_lens_val (numpy.ndarray): Each row represents the lengths of
            descriptions of a recipe in the validate set. The lengths are those
            that are returned by `dataset.Dataset.load_validate` method.
        seq_lens_test (numpy.ndarray): Each row represents the lengths of
            descriptions of a recipe in the test set. The lengths are those
            that are returned by `dataset.Dataset.load_test` method.
    """

    def __init__(self, config, path, stem=True):
        self.labels_map = {}
        self.labels_reverse_map = {}

        self.config = config
        self.network = None
        self._session = None
        """`tf.Session`: `Tensorflow` session linked to this
        :class:`Model` instance."""
        self._saver = None
        """`tf.train.Saver`: `Tensorflow` Saver instance that can be used to
        checkpoint and restore the `self._session` or a subset of
        `tf.Variables` linked to the `Model` instance."""

        self.stem = stem
        self._dataset = Dataset(stem=self.stem, config=self.config)
        """`dataset.Dataset`: Instance of Dataset class to handle loading and
        pre-processing of dataset for the model."""

        self.x_train = np.array([])
        self.x_validate = np.array([])
        self.x_test = np.array([])
        self.y_train = np.array([])
        self.y_validate = np.array([])
        self.y_test = np.array([])

        self.seq_lens_train = np.array([])
        self.seq_lens_val = np.array([])
        self.seq_lens_test = np.array([])

        self._path = path
        """`str`: Path of experiment directory"""

    def load_train_dataset(
            self, use_train_set, use_triggers_api, use_actions_api,
            use_synthetic_recipes, use_names_descriptions, load_vocab=False):
        """Loads dataset for training.

        Args:
            use_train_set (bool): Set to `True` if the original train set is to
                be loaded.
            use_triggers_api (bool): Set to `True` if the dataset constructed
                from Triggers API is to be loaded.
            use_actions_api (bool): Set to `True` if the dataset constructed
                from Actions API is to be loaded.
            use_synthetic_recipes (bool): Set to `True` if the synthetic recipes
                constructed from Triggers and Actions API are to be loaded.
            use_names_descriptions (bool): Set to `True` if both
                "name" and "description" field of recipes is to be used to
                construct descriptions of recipes.
            load_vocab (bool, optional): Set to `True` if vocabulary should be
                loaded from a pickle dump instead of being constructed from the
                dataset. This is usually done when resuming training on a stored
                model. Defaults to `False`, in which case, vocabulary will be
                built from the dataset loaded for training.
        """
        logging.debug("Loading dataset.")
        train_inputs, train_labels, train_seq_lens = self._dataset.load_train(
            vocab_path=self._path + VOCAB_FILE,
            use_train_set=use_train_set, use_triggers_api=use_triggers_api,
            use_actions_api=use_actions_api,
            use_synthetic_recipes=use_synthetic_recipes,
            use_names_descriptions=use_names_descriptions,
            load_vocab=load_vocab)
        logging.info("Train set loaded. Size = %s", len(train_inputs))
        validate_inputs, val_labels, val_seq_lens = self._dataset.load_validate(
            use_names_descriptions)
        logging.info("Validate set loaded.Size = %s", len(validate_inputs))

        self.x_train = np.array(train_inputs)
        self.x_validate = np.array(validate_inputs)

        self._create_label_maps()

        self.y_train = self._convert_to_one_hot(train_labels)
        self.y_validate = self._convert_to_one_hot(val_labels)

        self.seq_lens_train = np.array(train_seq_lens)
        self.seq_lens_val = np.array(val_seq_lens)

    def load_labels_and_vocab(self):
        """Loads vocabulary and mapping of labels to ids.

        `self.labels_map`, `self.labels_reverse_map`, and `self._database.vocab`
        are populated.
        """
        self._dataset.load_vocabulary(self._path + VOCAB_FILE)
        self._create_label_maps()

    def load_test_dataset(self, use_full_test_set=True, use_english=False,
                          use_english_intelligible=False,
                          use_gold=False, use_names_descriptions=False):
        """Loads dataset for testing.

         The specified subset of test data is loaded. Exactly one of the four
        arguments `use_full_test_set`, `use_use_english`, `use_gold`, and
        `use_use_english_intelligible` must be `True` indicating the desired
        subset to load.

        Args:
            use_names_descriptions (bool, optional): Set to `True` if both
                "name" and "description" field of recipes is to be used to
                construct descriptions of recipes. Defaults to `False`.
            use_gold (bool, optional): Set to `True` if only the gold subset of
                the test set is to be used for testing. Defaults to `False`.
            use_english_intelligible (bool, optional): Set to `True` if only
                that subset of the test set is to be used that is both English
                and intelligible. Defaults to `False`.
            use_english (bool, optional): Set to `True` if only the English
                subset of the test set is to be used for testing.
                Defaults to `False`.
            use_full_test_set (bool, optional): Set to `True` if the complete
                test set is to be used for testing. Defaults to `True`.
        """
        logging.debug("Loading dataset.")
        test_inputs, test_labels, test_seq_lens = self._dataset.load_test(
            use_full_test_set=use_full_test_set, use_english=use_english,
            use_english_intelligible=use_english_intelligible,
            use_gold=use_gold, use_names_descriptions=use_names_descriptions)
        logging.info("Test set loaded. Size = %s", len(test_inputs))
        self.x_test = np.array(test_inputs)
        self.y_test = self._convert_to_one_hot(test_labels)
        self.seq_lens_test = np.array(test_seq_lens)

    def initialize_network(self, init_variables=True, graph=None):
        """Constructs and initializes the Recurrent Neural Network.

        Additionally, creates the `Tensorflow` session and saver variables.

        Args:
            init_variables(bool, optional): Set to `True` if the variables
                created in the network should be initialized. Normally, this
                would be set to `False` when restoring a stored model.
                Defaults to `True`.
            graph (`tf.Graph`, optional): The `Tensorflow Graph` to be used to
                create the network and to be associated with the `Session`
                to be launched. Defaults to `None`, in which case the default
                `Graph` will be used.
        """
        logging.debug("Creating network.")
        self.network = LatentAttentionNetwork(config=self.config,
                                              num_classes=len(self.labels_map))
        logging.info("Network created.")
        self._session = tf.Session(graph=graph)
        if init_variables:
            self._session.run(tf.initialize_all_variables())
            logging.info("Variables initialized.")
        self._saver = tf.train.Saver(max_to_keep=None)

    def train(self):
        """Trains the network on the loaded training dataset using mini-batch
        optimization.
        """
        logging.debug("Starting training.")
        train_errors, validate_errors = [], []
        train_losses, validate_losses = [], []

        for epoch in xrange(1, self.config.num_epochs + 1):
            logging.debug("Starting epoch %s", epoch)
            for minibatch_indices in self._iterate_minibatches(
                    self.config.batch_size):
                feed_dict = self._feed_dictionary(
                    self.x_train, self.y_train, self.seq_lens_train,
                    self.config.dropout, minibatch_indices)
                self._session.run(self.network.optimize, feed_dict)

            # Evaluate and checkpoint the model at regular intervals.
            if epoch % EVALUATION_FREQ == 0 or epoch == self.config.num_epochs:
                # Log and plot errors and losses.
                self._log_errors(epoch, train_errors, validate_errors)
                self._log_losses(epoch, train_losses, validate_losses)

                # Checkpoint the model.
                self._checkpoint(epoch)

                # Check if forced-early-stop is requested.
                if self._stop(epoch):
                    logging.info("Epoch = %s. Forced stop received.", epoch)
                    break
            else:
                logging.info("Epoch = %s complete.", epoch)
        # Training complete. Perform session cleanup before exiting.
        self._post_training_cleanup()

    def restore(self, model_path):
        """Restores a saved model.

        The weights of an already created network are initialized with the
        values saved in the checkpoint at `model_path`.

        Args:
            model_path(str): Path of model checkpoint.
        """
        self._saver.restore(self._session, model_path)
        logging.info("Model loaded from checkpoint: %s", model_path)

    def evaluate(self):
        """Evaluates a trained model on the loaded test data.
        """
        logging.info("Starting evaluation.")
        test_error = self._test_error()
        logging.info("Test Error = %s", test_error)

    def predictions(self, inputs, seq_lens=None, preprocess=True):
        """Generates and returns predictions for given input descriptions.

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
            numpy.ndarray: Softmax output of the network.

        """
        # Pre-process the inputs if required. Otherwise, the inputs are assumed
        # to already be tokenized and pre-processed.
        if preprocess:
            inputs, seq_lens = self._dataset.preprocess_inputs(inputs)
        # Since we are predicting the labels and not evaluating the
        # predictions against true labels, we don't care about true labels -- in
        # fact, we don't have access to the true labels. Create dummy labels
        # to feed to the `tf.placeholder` corresponding to labels in the
        # network.
        dummy_labels = np.zeros(shape=(len(inputs), len(self.labels_map)))
        feed_dict = self._feed_dictionary(inputs, dummy_labels, seq_lens, 1.0)
        predictions = self._session.run(self.network.prediction, feed_dict)
        for i in xrange(len(predictions)):
            predictions[i] = softmax(predictions[i])
        return predictions

    def _convert_to_one_hot(self, labels):
        raise NotImplementedError("Abstract method")

    def _create_label_maps(self):
        raise NotImplementedError("Abstract method")

    def _load_label_maps(self, path):
        """Loads mapping between labels and ids.

        Args:
            path (str): Path of CSV file in which mapping is different.
        """
        with open(path, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['label'] in self.labels_map:
                    logging.error("Label `%s` already exists.", row['label'])
                    raise ValueError
                self.labels_map[row['label']] = int(row['id'])
                self.labels_reverse_map[int(row['id'])] = row['label']

        logging.info("Created `labels_map` and `labels_reverse_map`.")

    def _feed_dictionary(self, inputs, labels, seq_lens, dropout, indices=None):
        """Creates and returns the feed-dictionary required to run tf operations

        The feed-dictionary maps Tensorflow placeholders in the network to
        `numpy.ndarray`s or `list`s which should be used to feed values to the
        placeholders to conduct Tensorflow operations on the graph.

        Args:
            inputs (numpy.ndarray): Input to the network.
            labels (numpy.ndarray): True labels for the inputs.
            seq_lens (numpy.ndarray): Lengths of inputs to be used to
                appropriately unroll the RNN.
            dropout (float): Value of dropout to be used for RNN. A value of 1.0
                indicates no dropout.
            indices (list, optional): The indices of `inputs`, `labels`, and
                `seq_lens` to be fed to the network. Defaults to `None`, in
                which case the entirety of them will be used.

        Returns:
            dict: A dictionary that can be used as "feed-dictionary" to load
            values in network's `tf.placeholders` to perform desired operations.
        """
        feed_dict = dict()
        if indices is None:
            feed_dict[self.network.inputs] = inputs
            feed_dict[self.network.labels] = labels
            feed_dict[self.network.seq_lens] = seq_lens
        else:
            feed_dict[self.network.inputs] = inputs[indices]
            feed_dict[self.network.labels] = labels[indices]
            feed_dict[self.network.seq_lens] = seq_lens[indices]

        feed_dict[self.network.dropout] = dropout
        return feed_dict

    def _iterate_minibatches(self, batch_size, shuffle=True):
        """Yields list of indices for each mini-batch.

        The last mini-batch is not used because it, usually, has a different
        size. Since training set is shuffled before creating mini-batches, the
        training examples in the ignored mini-batches are used in  some other
        mini-batch in, at least, one epoch with high probability.

        Args:
            batch_size (int): Size of each mini-batch.
            shuffle (bool, optional): Set to `True` if the training set should
                be shuffled before each epoch. Defaults to `True`.

        Yields:
            list: List of indices corresponding to a mini-batch.
        """
        num_input = self.x_train.shape[0]
        indices = np.arange(num_input)
        if shuffle:
            np.random.shuffle(indices)
        for start_idx in range(0, num_input - batch_size + 1, batch_size):
            minibatch = indices[start_idx:start_idx + batch_size]
            yield minibatch

    def _log_errors(self, epoch, train_errors, validate_errors):
        """Logs current errors on training and validation sets.

        Additionally, the current errors are added to the list of errors
        `train_errors` and `validate_errors`.

        Args:
            epoch (int): Epoch number.
            train_errors (`list` of `float`): Training errors.
            validate_errors (`list` of `float`): Validation errors.
        """
        train_error = self._training_error()
        validate_error = self._validation_error()
        logging.info("Epoch = %s complete. Train Error = %s, "
                     "Validate Error = %s", epoch, train_error, validate_error)

        # Add errors to the accumulated errors lists for plotting.
        train_errors.append(train_error)
        validate_errors.append(validate_error)
        self._plot_errors(train_errors, validate_errors)
        logging.info("Epoch = %s. Error plots saved.", epoch)

    def _log_losses(self, epoch, train_losses, validate_losses):
        """Logs current losses on training and validation sets.

        Additionally, the current losses are added to the list of losses
        `train_losses` and `validate_losses`.

        Args:
            epoch (int): Epoch number.
            train_losses (`list` of `float`): Training losses.
            validate_losses (`list` of `float`): Validation losses.
        """
        train_loss = self._training_loss()
        validate_loss = self._validation_loss()
        logging.info("Epoch = %s complete. Train Loss = %s, "
                     "Validate Loss = %s", epoch, train_loss, validate_loss)

        # Add losses to the accumulated losses lists for plotting.
        train_losses.append(train_loss)
        validate_losses.append(validate_loss)
        self._plot_losses(train_losses, validate_losses)
        logging.info("Epoch = %s. Loss plots saved.", epoch)

    def _training_error(self):
        """Computes model's error on the training set.

        Returns:
            float: Model's error on the training set.
        """
        feed_dict = self._feed_dictionary(
            self.x_train, self.y_train, self.seq_lens_train,
            self.config.dropout)
        return self._session.run(self.network.error, feed_dict)

    def _validation_error(self):
        """Computes model's error on the validation set.

        Returns:
            float: Model's error on the validation set.
        """
        feed_dict = self._feed_dictionary(self.x_validate, self.y_validate,
                                          self.seq_lens_val, 1.0)
        return self._session.run(self.network.error, feed_dict)

    def _test_error(self):
        """Computes model's error on the test set.

        Returns:
            float: Model's error on the test set.
        """
        feed_dict = self._feed_dictionary(self.x_test, self.y_test,
                                          self.seq_lens_test, 1.0)
        return self._session.run(self.network.error, feed_dict)

    def _training_loss(self):
        """Computes model's loss on the training set.

        Returns:
            float: Model's loss on the training set.
        """
        feed_dict = self._feed_dictionary(self.x_train, self.y_train,
                                          self.seq_lens_train,
                                          self.config.dropout)
        return self._session.run(self.network.loss, feed_dict)

    def _validation_loss(self):
        """Computes model's loss on the validation set.

        Returns:
            float: Model's loss on the validation set.
        """
        feed_dict = self._feed_dictionary(self.x_validate, self.y_validate,
                                          self.seq_lens_val, 1.0)
        return self._session.run(self.network.loss, feed_dict)

    def _plot_errors(self, train_errors, validate_errors):
        """Plots training and validation errors.

        Args:
            train_errors (`list` of `float`): Training errors.
            validate_errors (`list` of `float`): Validation errors.
        """
        figure_path = self._path + "plots/train-validation-error-curve"
        x = [e * EVALUATION_FREQ for e in xrange(1, len(train_errors) + 1)]
        fig, ax = plt.subplots(1, 1)
        ax.set_xlabel('Number of epochs of training')
        ax.set_ylabel('Error')
        plt.plot(x, train_errors, 'r', label='training')
        plt.plot(x, validate_errors, 'b', label='validation')
        plt.legend(loc="best", framealpha=0.3)
        fig.savefig(figure_path)
        plt.close('all')

    def _plot_losses(self, train_losses, validate_losses):
        """Plots training and validation losses.

        Args:
            train_losses (`list` of `float`): Training losses.
            validate_losses (`list` of `float`): Validation losses.
        """
        figure_path = self._path + "plots/train-validation-loss-curve"
        x = [e * EVALUATION_FREQ for e in xrange(1, len(train_losses) + 1)]
        fig, ax = plt.subplots(1, 1)
        ax.set_xlabel('Number of epochs of training')
        ax.set_ylabel('Cross-entropy loss')
        plt.plot(x, train_losses, 'r', label='training')
        plt.plot(x, validate_losses, 'b', label='validation')
        plt.legend(loc="best", framealpha=0.3)
        fig.savefig(figure_path)
        plt.close('all')

    def _checkpoint(self, epoch):
        """Saves a checkpoint of the model.

        Args:
            epoch (int): Epoch number, to be used to name the checkpoint file.
        """
        self._saver.save(self._session, self._path + "model-checkpoints/model",
                         global_step=epoch)
        logging.info("Epoch = %s. Checkpoint dumped.", epoch)

    def _post_training_cleanup(self):
        """Runs cleanup operations after training is complete.

        The operations performed are:
            1. Delete the tf graph.
            2. Close tf session.
        """
        logging.info("Performing post-training cleanup.")
        tf.reset_default_graph()
        self._session.close()

    def _stop(self, epoch):
        """Reads the "stop-file" to check if forced-early-stop is requested.

        The training can be prematurely -- and cleanly -- stopped by writing
        "stop" (without quotes) in the "stop-file" located at `STOP_FILE`. This
        method reads the file to check if such a forced-early-stop is requested.

        Args:
            epoch (int): Epoch number, used only for logging purposes.

        Returns:
            bool: `True` if forced-early-stop is requested.
        """
        logging.info("Epoch = %s. Reading 'stop-file'", epoch)
        text = "default"
        try:
            fin = open(STOP_FILE, 'r')
            text = fin.read()
        except Exception as e:
            logging.warning("Epoch = %s. Unable to read 'Stop-file' at %s. "
                            "Exception: %s", epoch, STOP_FILE, e)
            pass
        finally:
            return "stop" in text
