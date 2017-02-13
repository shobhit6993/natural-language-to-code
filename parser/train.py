"""
Train a model on train set.
"""

import logging

from parser.action_channel_model import ActionChannelModel
from parser.action_function_model import ActionFunctionModel
from parser.argument_parser import training_arguments_parser
from parser import configs
from parser.constants import RNN_EXPT_DIRECTORY
from parser.trigger_function_model import TriggerFunctionModel
from parser.trigger_channel_model import TriggerChannelModel
from parser import utils


def parse_args():
    """Parses and logs command-line arguments.

    Returns:
        Namespace: Namespace containing parsed arguments.
    """
    args = training_arguments_parser().parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(levelname)s: %(asctime)s: %(message)s')
    logging.info("Log Level: %s", args.log_level)
    logging.info("Experiment Name: %s", args.experiment_name[0])
    logging.info("Model: %s", args.model[0])
    logging.info("Use Train Set: %s", args.use_train_set)
    logging.info("Use Triggers API: %s", args.use_triggers_api)
    logging.info("Use Actions API: %s", args.use_actions_api)
    logging.info("Use Synthetic Recipes: %s", args.use_synthetic_recipes)
    logging.info("Use Names and Descriptions: %s", args.use_names_descriptions)
    logging.info("Load and Train: %s", args.load_and_train)
    try:
        logging.info("Saved Model Path: %s", args.saved_model_path[0])
    except IndexError:
        pass

    return args


def log_configurations(config):
    """Logs the configurations being used.

    Configurations refer to the values for various hyper-parameters of the
    model.

    Args:
        config: A configuration class, similar to `configs.PaperConfigurations`.
    """
    logging.info("Using the following configurations:")
    logging.info("dropout = %s", config.dropout)
    logging.info("learning_rate = %s", config.learning_rate)
    logging.info("max_gradient_norm = %s", config.max_gradient_norm)
    logging.info("hidden_size (d) = %s", config.hidden_size)
    logging.info("batch_size = %s", config.batch_size)
    logging.info("vocab_size (N) = %s", config.vocab_size)
    logging.info("sent_size (j) = %s", config.sent_size)
    logging.info("num_epochs = %s", config.num_epochs)


def train_model(args, model_class, expt_path):
    """Trains a model defined by the `model_class` and `args` on train set.

    Args:
        expt_path (str): Path of experiment directory.
        args (Namespace): Namespace containing parsed arguments
        model_class (:obj:`Model`): One of the child classes of the `Model`
            class.
    """
    config = configs.PaperConfiguration
    log_configurations(config)
    model = model_class(config, expt_path, stem=True)
    model.load_train_dataset(use_train_set=args.use_train_set,
                             use_triggers_api=args.use_triggers_api,
                             use_actions_api=args.use_actions_api,
                             use_synthetic_recipes=args.use_synthetic_recipes,
                             use_names_descriptions=args.use_names_descriptions)
    model.initialize_network()
    model.train()


def load_and_train(args, model_class, expt_path):
    """Loads a pre-trained model and resumes training.

    Args:
        expt_path (str): Path of experiment directory.
        args (Namespace): Namespace containing parsed arguments
        model_class (:obj:`Model`): One of the child classes of the `Model`
            class.
    """
    config = configs.PaperConfiguration
    log_configurations(config)
    model = model_class(config, expt_path, stem=True)
    model.load_train_dataset(use_train_set=args.use_train_set,
                             use_triggers_api=args.use_triggers_api,
                             use_actions_api=args.use_actions_api,
                             use_synthetic_recipes=args.use_synthetic_recipes,
                             use_names_descriptions=args.use_names_descriptions,
                             load_vocab=True)
    model.initialize_network(init_variables=False)
    model.restore(args.saved_model_path[0])
    model.train()


def main():
    args = parse_args()
    utils.create_experiment_directory(args.experiment_name[0])

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

    expt_path = RNN_EXPT_DIRECTORY + args.experiment_name[0] + "/"
    if args.load_and_train:
        load_and_train(args, model_class, expt_path)
    else:
        train_model(args, model_class, expt_path)


if __name__ == '__main__':
    main()
