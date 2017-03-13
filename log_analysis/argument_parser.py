import argparse


def arguments_parser():
    """Parses command-line arguments for log analysisz.

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