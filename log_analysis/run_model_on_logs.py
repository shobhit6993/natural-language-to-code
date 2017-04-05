from __future__ import absolute_import

import glob
import logging

from dialog.configs import DialogConfiguration
from dialog.run_pipeline import create_dialog_agent, load_parsers
from log_analysis.argument_parser import model_on_logs_arguments_parser
from log_analysis.training_data_from_dialog import build_log_summaries


def parse_arguments():
    """Parses and logs command-line arguments.

    Returns:
        Namespace: Namespace containing parsed arguments.
    """
    args = model_on_logs_arguments_parser().parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(levelname)s: %(asctime)s: %(message)s')

    assert (args.log_directories != "")
    assert (args.alpha >= args.beta)

    DialogConfiguration.alpha = args.alpha
    DialogConfiguration.beta = args.beta

    logging.info("Log Level: %s", args.log_level)
    logging.info("Log directories: %s", args.log_directories)

    return args


class Interface(object):
    def __init__(self, conversation):
        self.conversation = conversation
        self.error = False

        self._sys_utterance = self._system_utterance_from_log()
        self._user_utterance = self._user_utterance_from_log()

    def get(self):
        if self.error:
            return "stop"

        utterance = self._user_utterance.next()
        return utterance

    def put(self, actual_sys_utterance):
        log_sys_utterance = self._sys_utterance.next()
        if log_sys_utterance != actual_sys_utterance:
            self.error = True

    def _system_utterance_from_log(self):
        for utterance in self.conversation.sys_utterances:
            yield utterance

    def _user_utterance_from_log(self):
        for utterance in self.conversation.user_utterances:
            yield utterance


def main():
    args = parse_arguments()
    log_files = glob.glob(args.log_directories + "/*.log")
    log_summaries = build_log_summaries(log_files)

    t_channel_parser, a_channel_parser, t_fn_parser, a_fn_parser, keyword_parser = load_parsers()

    for log_summary in log_summaries:
        n = len(log_summary.goals)
        for i in xrange(n):
            goal, conv = log_summary.goals[i], log_summary.conversations[i]
            # logging.info("Processing log with recipe: %s", goal.recipe_url)
            interface = Interface(conv)
            dialog_agent = create_dialog_agent(
                trigger_channel_parser=t_channel_parser,
                trigger_fn_parser=t_fn_parser,
                action_channel_parser=a_channel_parser,
                action_fn_parser=a_fn_parser,
                keyword_parser=keyword_parser, istream=interface,
                ostream=interface)
            dialog_agent.start_session()

            if interface.error:
                logging.info("Error in log with recipe: %s", goal.recipe_url)


if __name__ == '__main__':
    main()
