# Analyzes log files corresponding to Turk experiments.


from __future__ import absolute_import

import glob
import logging

from tracker.constants import DialogStatus
from log_analysis.experiment_statistics import ExperimentStatistics
from log_analysis.log_summary import LogSummary
from log_analysis.argument_parser import arguments_parser_log_analysis


def parse_arguments():
    """Parses and logs command-line arguments.

    Returns:
        Namespace: Namespace containing parsed arguments.
    """
    args = arguments_parser_log_analysis().parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(levelname)s: %(asctime)s: %(message)s')

    assert (args.log_directories != "")
    logging.info("Log Level: %s", args.log_level)
    logging.info("Log directories: %s", args.log_directories)

    return args


def build_log_summaries(log_files):
    """Generates summaries `LogSummary` of each log file in the list of log
    files, if possible.

    Args:
        log_files (`list` of `str`): List of log files' paths.

    Returns:
        `list` of `LogSummary`: List of log summaries. It might not contain
        a `LogSummary` instance for each log file, since some log files might
        be corrupt.
    """
    summaries = []
    for log_file in log_files:
        summary = LogSummary()
        if not summary.generate_summary(log_file):
            continue
        summary.generate_stats()
        summaries.append(summary)
    return summaries


def generate_expt_stats(log_summaries):
    """Generates experiment-level statistics by combining individual log-level
    statistics

    Args:
        log_summaries (`list` of `LogSummary`): List of log summaries whose
            statistics need to be combined.
    """
    experiment_stats = ExperimentStatistics()
    for summary in log_summaries:
        for dialog_stat in summary.dialog_stats:
            experiment_stats.increment_num_dialogs()

            experiment_stats.increment_total_dialog_length(
                dialog_stat.dialog_length)

            if dialog_stat.dialog_status_user_view is DialogStatus.success:
                experiment_stats.increment_num_successful_dialogs_user_view()
            elif dialog_stat.dialog_status_user_view is DialogStatus.terminated:
                experiment_stats.increment_num_terminated_dialogs()
            elif dialog_stat.dialog_status_user_view is DialogStatus.incomplete:
                experiment_stats.increment_num_terminated_dialogs()

            if dialog_stat.dialog_status_true is DialogStatus.success:
                experiment_stats.increment_num_successful_dialogs_true()

        for survey in summary.surveys:
            experiment_stats.increment_survey_easy_score(survey.easy)
            experiment_stats.increment_survey_understand_score(survey.understand)
            experiment_stats.increment_survey_sensible_score(survey.sensible)
            experiment_stats.increment_survey_long_score(survey.long)

    return experiment_stats


def print_expt_statistics(expt_stats):
    """Prints experiment-level statistics.

    Args:
        expt_stats (ExperimentStatistics): Experiment-level statistics.
    """
    print "-----------"
    print "Average Dialog Length: ", expt_stats.dialog_length
    print ("Fraction of Successful Dialogs (user's view): ",
           expt_stats.successful_dialogs_user_view)
    print ("Fraction of Successful Dialogs (true): ",
           expt_stats.successful_dialogs_true)
    print "Fraction of Terminated Dialogs: ", expt_stats.terminated_dialogs
    print "Fraction of Incomplete Dialogs: ", expt_stats.incomplete_dialogs
    print "-----------"
    print "Average Score for 'easy': ", expt_stats.survey_easy_score
    print "Average Score for 'understand': ", expt_stats.survey_understand_score
    print "Average Score for 'sensible': ", expt_stats.survey_sensible_score
    print "Average Score for 'long': ", expt_stats.survey_long_score


def main():
    args = parse_arguments()
    log_files = glob.glob(args.log_directories + "/*.log")
    log_summaries = build_log_summaries(log_files)
    expt_stats = generate_expt_stats(log_summaries)
    print_expt_statistics(expt_stats)


if __name__ == '__main__':
    main()
