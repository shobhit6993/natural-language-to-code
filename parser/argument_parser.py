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
    parser.add_argument('--use-full-test-set', action='store_true',
                        help="Use the entire test set for testing.",
                        dest='use_full_test_set')
    parser.add_argument('--use-english', action='store_true',
                        help="Use the English-only subset of test set for "
                             "testing.", dest='use_english')
    parser.add_argument('--use-english-intelligible', action='store_true',
                        help="Use the English-and-intelligible subset of test "
                             "set for testing.",
                        dest='use_english_intelligible')
    parser.add_argument('--use-gold', action='store_true',
                        help="Use the gold subset of test set for testing.",
                        dest='use_gold')
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
