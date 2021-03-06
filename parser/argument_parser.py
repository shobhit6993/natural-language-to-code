import argparse


def training_arguments_parser():
    """Parses command-line arguments for training.

    Returns:
        argparse.ArgumentParser: Argument parser for training
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--log-level', nargs='?', type=str,
                        default="INFO", const="INFO",
                        help="Logging level. Can take values among ['DEBUG',"
                             "'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
                        dest='log_level')
    parser.add_argument('--model', nargs=1, type=str,
                        help="Model class to be used", dest='model')
    parser.add_argument('--experiment-name', nargs=1, type=str,
                        help="Name of the experiment to be used to name "
                             "the experiment's directory",
                        dest='experiment_name')
    parser.add_argument('--load-and-train', action='store_true',
                        help="Load a saved model and continue training.",
                        dest='load_and_train')
    parser.add_argument('--retrain', nargs='?', type=str,
                        default="all", const="all",
                        help="Which model parameters to be learned during "
                             "re-training. Can take values among ['all',"
                             "'non-attention', 'attention']. Defaults to 'all'."
                             " Relevant only with --load-and-train option. In "
                             "simple training case, all parameters are "
                             "learned.",
                        dest='retrain')
    parser.add_argument('--saved-model-path', nargs='?', type=str,
                        default="", const="",
                        help="Path of the saved model to be loaded.",
                        dest='saved_model_path')
    parser.add_argument('--use-train-set', action='store_true',
                        help="Use data from training set for training.",
                        dest='use_train_set')
    parser.add_argument('--use-triggers-api', action='store_true',
                        help="Use data from Triggers API for training.",
                        dest='use_triggers_api')
    parser.add_argument('--use-actions-api', action='store_true',
                        help="Use data from Actions API for training.",
                        dest='use_actions_api')
    parser.add_argument('--use-synthetic-recipes', action='store_true',
                        help="Use data from synthetic recipes for training.",
                        dest='use_synthetic_recipes')
    parser.add_argument('--external-train-csv', nargs='?', type=str,
                        default="", const="",
                        help="Path of a CSV file from which train set is to be "
                             "loaded. Use this only if you want to load the "
                             "train set from an external CSV file, potentially"
                             "in addition to the default IFTTT train set.",
                        dest='external_train_csv')
    parser.add_argument('--use-names-descriptions', action='store_true',
                        help="Use both names and descriptions of recipes.",
                        dest='use_names_descriptions')

    return parser


def testing_arguments_parser():
    """Parses command-line arguments for testing.

    Returns:
        argparse.ArgumentParser: Argument parser for testing.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--log-level', nargs='?', type=str,
                        default="INFO", const="INFO",
                        help="Logging level. Can take values among ['DEBUG',"
                             "'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
                        dest='log_level')
    parser.add_argument('--model', nargs=1, type=str,
                        help="Model class to be used", dest='model')
    parser.add_argument('--experiment-name', nargs='*', type=str,
                        help="Name of the experiment that was used for "
                             "training", dest='experiment_name')
    parser.add_argument('--saved-model-path', nargs='*', type=str,
                        help="Path of the saved model to be tested.",
                        dest='saved_model_path')
    parser.add_argument('--external-test-csv', nargs='?', type=str,
                        default="", const="",
                        help="Path of a CSV file from which test set is to be "
                             "loaded. Use this only if you want to load the "
                             "test set from an external CSV file, and not use "
                             "the default IFTTT test set.",
                        dest='external_test_csv')
    parser.add_argument('--use-full-test-set', action='store_true',
                        help="Use the entire IFTTT test set for testing. "
                             "Ignored if --external-test-csv is specified.",
                        dest='use_full_test_set')
    parser.add_argument('--use-english', action='store_true',
                        help="Use the English-only subset of IFTTT test set for"
                             " testing. Ignored if --external-test-csv is "
                             "specified.", dest='use_english')
    parser.add_argument('--use-english-intelligible', action='store_true',
                        help="Use the English-and-intelligible subset of the "
                             "IFTTT test set for testing. Ignored if "
                             "--external-test-csv is specified.",
                        dest='use_english_intelligible')
    parser.add_argument('--use-gold', action='store_true',
                        help="Use the gold subset of IFTTT test set for "
                             "testing. Ignored if --external-test-csv is "
                             "specified.", dest='use_gold')
    parser.add_argument('--use-names-descriptions', action='store_true',
                        help="Use both names and descriptions of recipes.",
                        dest='use_names_descriptions')

    return parser


def prediction_arguments_parser():
    """Parses command-line arguments for prediction.

    Returns:
        argparse.ArgumentParser: Argument parser for prediction.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--log-level', nargs='?', type=str,
                        default="INFO", const="INFO",
                        help="Logging level. Can take values among ['DEBUG',"
                             "'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
                        dest='log_level')
    parser.add_argument('--model', nargs=1, type=str,
                        help="Model class to be used", dest='model')
    parser.add_argument('--experiment-name', nargs='*', type=str,
                        help="Name of the experiment that was used for "
                             "training", dest='experiment_name')
    parser.add_argument('--saved-model-path', nargs='*', type=str,
                        help="Path of the saved model to be tested.",
                        dest='saved_model_path')

    return parser
