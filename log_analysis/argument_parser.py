import argparse


def arguments_parser_log_analysis():
    """Parses command-line arguments for log analysis.

    Returns:
        argparse.ArgumentParser: Argument parser for training
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', nargs='?', type=str,
                        default="INFO", const="INFO",
                        help="Logging level. Can take values among ['DEBUG',"
                             "'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
                        dest='log_level')
    parser.add_argument('--log-directories', nargs='?', type=str,
                        default="", const="",
                        help="Directories containing log files.",
                        dest='log_directories')
    return parser


def arguments_parser_training_data():
    """Parses command-line arguments for log analysis.

    Returns:
        argparse.ArgumentParser: Argument parser for training
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', nargs='?', type=str,
                        default="INFO", const="INFO",
                        help="Logging level. Can take values among ['DEBUG',"
                             "'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
                        dest='log_level')
    parser.add_argument('--log-directories', nargs='?', type=str,
                        default="", const="",
                        help="Directories containing log files.",
                        dest='log_directories')
    parser.add_argument('--generate-full-pos', nargs='?', type=str,
                        default="", const="",
                        help="File where positive training data-points "
                             "generated in the IFTTT corpus format.",
                        dest='generate_full_pos')
    parser.add_argument('--generate-t-channel-neg', nargs='?', type=str,
                        default="", const="",
                        help="File where negative training data-points "
                             "generated for Trigger Channel model should be "
                             "written to, if specified.",
                        dest='generate_t_channel_neg')
    parser.add_argument('--generate-a-channel-neg', nargs='?', type=str,
                        default="", const="",
                        help="File where negative training data-points "
                             "generated for Action Channel model should be "
                             "written to,  if specified.",
                        dest='generate_a_channel_neg')
    parser.add_argument('--generate-t-fn-neg', nargs='?', type=str,
                        default="", const="",
                        help="File where negative training data-points "
                             "generated for Trigger Function model should be "
                             "written to,  if specified.",
                        dest='generate_t_fn_neg')
    parser.add_argument('--generate-a-fn-neg', nargs='?', type=str,
                        default="", const="",
                        help="File where negative training data-points "
                             "generated for Action Function model should be "
                             "written to,  if specified.",
                        dest='generate_a_fn_neg')
    parser.add_argument('--generate-t-fn-pos', nargs='?', type=str,
                        default="", const="",
                        help="File where positive training data-points "
                             "generated for Trigger Function model should be "
                             "written to,  if specified.",
                        dest='generate_t_fn_pos')
    parser.add_argument('--generate-a-fn-pos', nargs='?', type=str,
                        default="", const="",
                        help="File where positive training data-points "
                             "generated for Action Function model should be "
                             "written to,  if specified.",
                        dest='generate_a_fn_pos')
    return parser