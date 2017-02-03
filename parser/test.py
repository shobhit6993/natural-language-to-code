"""
Evaluate a single model or an ensemble of models on test data.
"""

import logging
import tensorflow as tf

from action_channel_model import ActionChannelModel
from action_function_model import ActionFunctionModel
from argument_parser import testing_arguments_parser
import configs
from constants import RNN_EXPT_DIRECTORY
from ensembled_model import EnsembledModel
from trigger_function_model import TriggerFunctionModel
from trigger_channel_model import TriggerChannelModel
import utils


def parse_args():
    """Parses and logs command-line arguments.

    Returns:
        Namespace: Namespace containing parsed arguments.
    """
    args = testing_arguments_parser().parse_args()

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
    logging.info("Use Names and Descriptions: %s", args.use_names_descriptions)

    return args


def log_configurations(config):
    """Logs the configurations being used.

    Configurations refer to the values for various hyper-parameters of the
    model.

    Args:
        config: A configuration class, similar to `configs.PaperConfigurations`.
    """
    logging.info("Using the following configurations:")
    logging.info("hidden_size (d) = %s", config.hidden_size)
    logging.info("vocab_size (N) = %s", config.vocab_size)
    logging.info("sent_size (j) = %s", config.sent_size)


def test_ensemble(models):
    """Evaluate an ensemble of multiple models.

    If n models are supplied, a total of n ensembles -- one for each ensemble
    size -- are evaluated.

    Args:
        models (`list` of `model.Model`): Models to be ensembled.
    """
    num_models = len(models)
    for ensemble_size in xrange(1, num_models + 1):
        # Evaluate ensemble of `ensemble_size` models
        logging.info("Evaluating an ensemble of %s models", ensemble_size)
        ensemble = EnsembledModel()
        for i in xrange(ensemble_size):
            ensemble.add_model(models[i])
        ensemble.evaluate()


def test_models(args, model_class):
    """Evaluates model(s) defined by the `model_class` and `args` on test set.

     The model(s) is (are) first created and loaded from the specified
     checkpoints, and then evaluated on the specified subset of the test set.

    Args:
        args (Namespace): Namespace containing parsed arguments
        model_class (:obj:`Model`): One of the child classes of the `Model`
            class.
    """
    assert(len(args.experiment_name) == len(args.saved_model_path))
    config = configs.PaperConfiguration
    log_configurations(config)

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
            model.evaluate()
            models.append(model)

    test_ensemble(models)


def main():
    args = parse_args()
    utils.verify_experiment_directory(args.experiment_name[0])

    if args.model[0] == "TriggerFunctionModel":
        model_class = TriggerFunctionModel
    elif args.model[0] == "ActionFunctionModel":
        model_class = ActionFunctionModel
    elif args.model[0] == "TriggerChannelModel":
        model_class = TriggerChannelModel
    elif args.model[0] == "ActionChannelModel":
        model_class = ActionChannelModel
    else:
        logging.error("Illegal model class %s", args.model[0])
        return

    test_models(args, model_class)


if __name__ == '__main__':
    main()
