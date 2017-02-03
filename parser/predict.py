"""
Generate predictions online using a model loaded from a checkpoint.
"""

import logging
import tensorflow as tf

from action_channel_model import ActionChannelModel
from action_function_model import ActionFunctionModel
from argument_parser import prediction_arguments_parser
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
    args = prediction_arguments_parser().parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(levelname)s: %(asctime)s: %(message)s')
    logging.info("Log Level: %s", args.log_level)
    logging.info("Experiment Name: %s", args.experiment_name)
    logging.info("Model: %s", args.model[0])
    logging.info("Saved Model Path: %s", args.saved_model_path)

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


def prepare_models_for_predictions(args, model_class):
    """Prepares the models for predictions by creating the network, restoring
    the learned weights, and loading vocabulary and label mappings.

    Args:
        args (Namespace): Namespace containing parsed arguments.
        model_class (:obj:`Model`): One of the child classes of the `Model`
            class.

    Returns:
        `list` of `model.Model`: List of restored models.

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
            model.initialize_network(init_variables=False, graph=graph)
            model.restore(args.saved_model_path[i])
            models.append(model)
    return models


def prediction_loop(models, k):
    # Create the ensemble.
    """Runs an infinite loop to consume user-input and spit-out predictions.

    Top-`k` predictions, along with associated probabilities, are printed.

    Args:
        models (`list` of `model.Model`): List of models to be ensembled.
        k (int): Number of top predictions to be printed.
    """
    ensemble = EnsembledModel()
    for i in xrange(len(models)):
        ensemble.add_model(models[i])
    logging.info("Models ready for prediction.")
    input = raw_input("Enter a description:")
    while input.lower() != "stop":
        predictions = ensemble.predict(input, k)
        print predictions
        input = raw_input("Enter a description:")


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

    models = prepare_models_for_predictions(args, model_class)
    k = 2
    prediction_loop(models, k)


if __name__ == '__main__':
    main()
