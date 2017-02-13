import logging
import numpy as np
import tensorflow as tf

from action_channel_model import ActionChannelModel
from action_function_model import ActionFunctionModel
import configs
from constants import RNN_EXPT_DIRECTORY
from ensembled_model import EnsembledModel
import parser.argument_parser as model_arg_parser
from trigger_function_model import TriggerFunctionModel
from trigger_channel_model import TriggerChannelModel


class CombinedModel(object):
    """Model class that combines different types of models -- such as
    `TriggerChannelModel`, `ActionChannelModel`, and `EnsembledModel` -- and
    exposes methods to enable them to be evaluated or used on the same set of
    examples or inputs.

    Attributes:
        use_trigger_channel_model (bool): Set to `True` if the trained
            `TriggerChannelModel` is to be included in the cocktail of models.
        use_action_channel_model (bool): Set to `True` if the trained
            `ActionChannelModel` is to be included in the cocktail of models.
        use_action_fn_model (bool): Set to `True` if the trained
            `ActionFunctionModel` is to be included in the cocktail of models.
        use_trigger_fn_model (bool): Set to `True` if the trained
            `TriggerFunctionModel` is to be included in the cocktail of models.
    """
    _t_channel_arg_str = "--log-level INFO --model TriggerChannelModel --experiment-name trigger-channel-1/trigger-channel-1-0 trigger-channel-1/trigger-channel-1-6 trigger-channel-1/trigger-channel-1-7 trigger-channel-1/trigger-channel-1-4 trigger-channel-1/trigger-channel-1-1 trigger-channel-1/trigger-channel-1-3 trigger-channel-1/trigger-channel-1-8 trigger-channel-1/trigger-channel-1-5 trigger-channel-1/trigger-channel-1-9 trigger-channel-1/trigger-channel-1-2 --use-names-descriptions --use-gold --saved-model-path ./experiments/rnn/trigger-channel-1/trigger-channel-1-0/model-18 ./experiments/rnn/trigger-channel-1/trigger-channel-1-6/model-21 ./experiments/rnn/trigger-channel-1/trigger-channel-1-7/model-14 ./experiments/rnn/trigger-channel-1/trigger-channel-1-4/model-23 ./experiments/rnn/trigger-channel-1/trigger-channel-1-1/model-19 ./experiments/rnn/trigger-channel-1/trigger-channel-1-3/model-16 ./experiments/rnn/trigger-channel-1/trigger-channel-1-8/model-14 ./experiments/rnn/trigger-channel-1/trigger-channel-1-5/model-24 ./experiments/rnn/trigger-channel-1/trigger-channel-1-9/model-14 ./experiments/rnn/trigger-channel-1/trigger-channel-1-2/model-18"
    _a_channel_arg_str = "--log-level INFO --model ActionChannelModel --experiment-name action-channel-1/action-channel-1-7/ action-channel-1/action-channel-1-2/ action-channel-1/action-channel-1-5/ action-channel-1/action-channel-1-0/ action-channel-1/action-channel-1-4/ action-channel-1/action-channel-1-9/ action-channel-1/action-channel-1-1/ action-channel-1/action-channel-1-6/ action-channel-1/action-channel-1-8/ action-channel-1/action-channel-1-3/ --use-names-descriptions --use-gold --saved-model-path ./experiments/rnn/action-channel-1/action-channel-1-7/model-15 ./experiments/rnn/action-channel-1/action-channel-1-2/model-13 ./experiments/rnn/action-channel-1/action-channel-1-5/model-14 ./experiments/rnn/action-channel-1/action-channel-1-0/model-10 ./experiments/rnn/action-channel-1/action-channel-1-4/model-15 ./experiments/rnn/action-channel-1/action-channel-1-9/model-13 ./experiments/rnn/action-channel-1/action-channel-1-1/model-10 ./experiments/rnn/action-channel-1/action-channel-1-6/model-15 ./experiments/rnn/action-channel-1/action-channel-1-8/model-14 ./experiments/rnn/action-channel-1/action-channel-1-3/model-11"
    _t_fn_arg_str = "--log-level INFO --model TriggerFunctionModel --experiment-name trigger-func-35/trigger-func-35-1 trigger-func-35/trigger-func-35-6 trigger-func-35/trigger-func-35-2 trigger-func-35/trigger-func-35-8 trigger-func-35/trigger-func-35-9 trigger-func-35/trigger-func-35-3 trigger-func-35/trigger-func-35-7 trigger-func-35/trigger-func-35-4 trigger-func-35/trigger-func-35-0 trigger-func-35/trigger-func-35-5 --use-names-descriptions --use-gold --saved-model-path ./experiments/rnn/trigger-func-35/trigger-func-35-1/model-20 ./experiments/rnn/trigger-func-35/trigger-func-35-6/model-20 ./experiments/rnn/trigger-func-35/trigger-func-35-2/model-21 ./experiments/rnn/trigger-func-35/trigger-func-35-8/model-21 ./experiments/rnn/trigger-func-35/trigger-func-35-9/model-19 ./experiments/rnn/trigger-func-35/trigger-func-35-3/model-18 ./experiments/rnn/trigger-func-35/trigger-func-35-7/model-21 ./experiments/rnn/trigger-func-35/trigger-func-35-4/model-19 ./experiments/rnn/trigger-func-35/trigger-func-35-0/model-19 ./experiments/rnn/trigger-func-35/trigger-func-35-5/model-17"
    _a_fn_arg_str = "--log-level INFO --model ActionFunctionModel --experiment-name action-func-1/action-func-1-6 action-func-1/action-func-1-1 action-func-1/action-func-1-8 action-func-1/action-func-1-4 action-func-1/action-func-1-2 action-func-1/action-func-1-7 action-func-1/action-func-1-9 action-func-1/action-func-1-0 action-func-1/action-func-1-5 action-func-1/action-func-1-3 --use-names-descriptions --use-gold --saved-model-path ./experiments/rnn/action-func-1/action-func-1-6/model-19 ./experiments/rnn/action-func-1/action-func-1-1/model-17 ./experiments/rnn/action-func-1/action-func-1-8/model-21 ./experiments/rnn/action-func-1/action-func-1-4/model-22 ./experiments/rnn/action-func-1/action-func-1-2/model-18 ./experiments/rnn/action-func-1/action-func-1-7/model-18 ./experiments/rnn/action-func-1/action-func-1-9/model-21 ./experiments/rnn/action-func-1/action-func-1-0/model-20 ./experiments/rnn/action-func-1/action-func-1-5/model-21 ./experiments/rnn/action-func-1/action-func-1-3/model-15"

    _arg_parser = model_arg_parser.testing_arguments_parser()
    t_channel_args = _arg_parser.parse_args(_t_channel_arg_str.split(' '))
    """`t_channel_args`: Parsed command-line arguments for loading an ensemble
            of `TriggerChannelModel` models."""
    a_channel_args = _arg_parser.parse_args(_a_channel_arg_str.split(' '))
    """`a_channel_args`: Parsed command-line arguments for loading an
            ensemble of `ActionChannelModel` models."""
    t_fn_args = _arg_parser.parse_args(_t_fn_arg_str.split(' '))
    """`t_fn_args`: Parsed command-line arguments for loading an ensemble of
            `TriggerFunctionModel` models."""
    a_fn_args = _arg_parser.parse_args(_a_fn_arg_str.split(' '))
    """`a_fn_args`: Parsed command-line arguments for loading an ensemble of
            `ActionFunctionModel` models."""

    def __init__(self, use_trigger_channel_model=True,
                 use_action_channel_model=True, use_trigger_fn_model=True,
                 use_action_fn_model=True):
        """Sets which types of models to include in the cocktail of models to be
        used together.

        Args:
            use_trigger_channel_model (bool): Add an ensemble of
                `TriggerChannelModel` models to the cocktail of models if
                `True`. Defaults to `True`.
            use_action_channel_model (bool): Add an ensemble of
                `ActionChannelModel` models to the cocktail of models if
                `True`. Defaults to `True`.:
            use_trigger_fn_model (bool): Add an ensemble of
                `TriggerFunctionModel` models to the cocktail of models if
                `True`. Defaults to `True`.:
            use_action_fn_model (bool): Add an ensemble of
                `ActionFunctionModel` models to the cocktail of models if
                `True`. Defaults to `True`.:
        """
        self.use_trigger_channel_model = use_trigger_channel_model
        self.use_action_channel_model = use_action_channel_model
        self.use_trigger_fn_model = use_trigger_fn_model
        self.use_action_fn_model = use_action_fn_model

    def test_models(self):
        """Evaluates the trained models on a common set of test examples.

         The models used are the ones for which the corresponding boolean is set
         to `True`.

        The evaluation is performed both individually and combined. This method
        can be used to evaluate different classes of models, such as
        `TriggerChannelModel` and `ActionChannelModel` on the common set of test
        examples, so as to determine their combined performance, such as the
        total error in predicting recipes' channels.
        """
        args, model_classes = [], []
        if self.use_trigger_channel_model:
            args.append(self.t_channel_args)
            model_classes.append(TriggerChannelModel)
        if self.use_action_channel_model:
            args.append(self.a_channel_args)
            model_classes.append(ActionChannelModel)
        if self.use_trigger_fn_model:
            args.append(self.t_fn_args)
            model_classes.append(TriggerFunctionModel)
        if self.use_action_fn_model:
            args.append(self.a_fn_args)
            model_classes.append(ActionFunctionModel)

        ensembles = []
        for arg, model_class in zip(args, model_classes):
            ensembles.append(self.create_ensemble(arg, model_class))

        n = len(ensembles[0].test_data()[0])
        mistakes = np.array([False] * n)
        for ensemble in ensembles:
            inputs, labels, seq_lens = ensemble.test_data()
            m = ensemble.prediction_mistakes(inputs, labels, seq_lens)
            logging.info("Individual error = %s", np.mean(m))
            mistakes = mistakes | m

        error = np.mean(mistakes)
        logging.info("Combined Error = %s", error)

    @staticmethod
    def create_ensemble(args, model_class):
        """Creates an ensemble of models defined by the `model_class` and passed
        command-line arguments `args`.

        The command-line arguments are used to create and restore desired models
        and subset of the test set.

        Args:
            args (Namespace): Namespace containing parsed arguments.
            model_class (:obj:`Model`): One of the child classes of the `Model`
                class.

        Returns:
            EnsembledModel: An ensembled model.
        """
        assert (len(args.experiment_name) == len(args.saved_model_path))
        config = configs.PaperConfiguration
        CombinedModel._log_configurations(config)

        num_models = len(args.experiment_name)
        models = []
        for i in xrange(num_models):
            with tf.Graph().as_default() as graph:
                logging.info("Model number %s", i)
                expt_path = RNN_EXPT_DIRECTORY + args.experiment_name[i] + "/"
                model = model_class(config, expt_path, stem=True)
                model.load_labels_and_vocab()
                model.load_test_dataset(
                    use_full_test_set=args.use_full_test_set,
                    use_english=args.use_english,
                    use_english_intelligible=args.use_english_intelligible,
                    use_gold=args.use_gold,
                    use_names_descriptions=args.use_names_descriptions)
                model.initialize_network(init_variables=False, graph=graph)
                model.restore(args.saved_model_path[i])
                models.append(model)

        ensemble = EnsembledModel()
        for model in models:
            ensemble.add_model(model)
        return ensemble

    def _log_args(self, args):
        """Logs command-line arguments."""
        logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                            format='%(levelname)s: %(asctime)s: %(message)s')
        logging.info("Log Level: %s", args.log_level)
        logging.info("Experiment Name: %s", args.experiment_name)
        logging.info("Model: %s", args.model[0])
        logging.info("Saved Model Path: %s", args.saved_model_path)
        logging.info("Use Full Test Set: %s", args.use_full_test_set)
        logging.info("Use English Subset: %s", args.use_english)
        logging.info("Use English and Intelligible Subset: %s",
                     args.use_english_intelligible)
        logging.info("Use Gold Subset: %s", args.use_gold)
        logging.info("Use Names and Descriptions: %s",
                     args.use_names_descriptions)

    @staticmethod
    def _log_configurations(self, config):
        """Logs the configurations being used.

        Configurations refer to the values for various hyper-parameters of the
        model.

        Args:
            config: A configuration class, similar to
            `configs.PaperConfigurations`.
        """
        logging.info("Using the following configurations:")
        logging.info("hidden_size (d) = %s", config.hidden_size)
        logging.info("vocab_size (N) = %s", config.vocab_size)
        logging.info("sent_size (j) = %s", config.sent_size)
