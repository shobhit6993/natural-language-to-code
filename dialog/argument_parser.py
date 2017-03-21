import argparse


def dialog_arguments_parser():
    """Parses command-line arguments for dialog agent.

    Returns:
        argparse.ArgumentParser: Argument parser for training
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--log-level', nargs='?', type=str,
                        default="INFO", const="INFO",
                        help="Logging level. Can take values among ['DEBUG',"
                             "'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
                        dest='log_level')
    parser.add_argument('--alpha', nargs='?', type=float,
                        default=0.85, const=0.85,
                        help="Threshold of confidence above which the slot is "
                             "deemed as confidently-filled without a need for "
                             "confirmation.", dest='alpha')
    parser.add_argument('--beta', nargs='?', type=float,
                        default=0.25, const=0.25,
                        help="Threshold of confidence above which -- and below"
                             " alpha -- above which the slot is explicitly "
                             "confirmed before being accepted", dest='beta')
    # Following are required only when running the dialog system against the
    # simulated user using `simulated_user.run_pipeline`
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
    return parser
