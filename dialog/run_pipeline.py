"""Runs the dialog pipeline by having creating a dialog agent and having it
engage in a conversation with a user through terminal.
"""

from __future__ import absolute_import

import logging

from dialog.argument_parser import dialog_arguments_parser
from dialog.configs import DialogConfiguration
from dialog.dialog_agent import DialogAgent
from dialog.dialog_policy import DialogPolicy
from dialog.dialog_state import DialogState
from dialog.input_output import Input, Output
from dialog.label_description import LabelDescription
from dialog.intention import Intention
from dialog.utterance_parser import UtteranceParser
from parser.action_channel_model import ActionChannelModel
from parser.action_function_model import ActionFunctionModel
from parser.combined_model import CombinedModel
from parser.keyword_model import KeywordModel
from parser.trigger_function_model import TriggerFunctionModel
from parser.trigger_channel_model import TriggerChannelModel
from tracker.dialog_tracker import DialogTracker


def parse_arguments():
    args = dialog_arguments_parser().parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(levelname)s: %(asctime)s: %(message)s')

    assert(args.alpha >= args.beta)
    DialogConfiguration.alpha = args.alpha
    DialogConfiguration.beta = args.beta


def load_trigger_channel_parser():
    args = CombinedModel.t_channel_args
    return CombinedModel.create_ensemble(args, TriggerChannelModel)


def load_action_channel_parser():
    args = CombinedModel.a_channel_args
    return CombinedModel.create_ensemble(args, ActionChannelModel)


def load_trigger_fn_parser():
    args = CombinedModel.t_fn_args
    return CombinedModel.create_ensemble(args, TriggerFunctionModel)


def load_action_fn_parser():
    args = CombinedModel.a_fn_args
    return CombinedModel.create_ensemble(args, ActionFunctionModel)


def load_keyword_parser():
    return KeywordModel()


def load_parsers():
    logging.debug("Loading parsers.")
    trigger_channel_parser = load_trigger_channel_parser()
    action_channel_parser = load_action_channel_parser()
    trigger_fn_parser = load_trigger_fn_parser()
    action_fn_parser = load_action_fn_parser()
    keyword_parser = load_keyword_parser()
    logging.info("All parsers loaded.")
    return (trigger_channel_parser, action_channel_parser, trigger_fn_parser,
            action_fn_parser, keyword_parser)


def create_dialog_agent(trigger_channel_parser, action_channel_parser,
                        trigger_fn_parser, action_fn_parser, keyword_parser,
                        istream, ostream):
    logging.info("Initializing dialog agent.")
    label_description = LabelDescription()
    parser = UtteranceParser(trigger_channel_model=trigger_channel_parser,
                             action_channel_model=action_channel_parser,
                             trigger_fn_model=trigger_fn_parser,
                             action_fn_model=action_fn_parser,
                             keyword_model=keyword_parser,
                             label_description=label_description)
    intention = Intention
    dialog_policy = DialogPolicy(DialogConfiguration)
    dialog_state = DialogState()
    tracker = DialogTracker()
    dialog_agent = DialogAgent(state=dialog_state, policy=dialog_policy,
                               parser=parser, intention=intention,
                               label_description=label_description,
                               istream=istream, ostream=ostream,
                               tracker=tracker)
    return dialog_agent


def main():
    parse_arguments()
    t_channel_parser, a_channel_parser, t_fn_parser, a_fn_parser, \
        keyword_parser = load_parsers()
    while True:
        dialog_agent = create_dialog_agent(
            trigger_channel_parser=t_channel_parser,
            trigger_fn_parser=t_fn_parser,
            action_channel_parser=a_channel_parser,
            action_fn_parser=a_fn_parser,
            keyword_parser=keyword_parser, istream=Input(), ostream=Output())
        dialog_agent.start_session()


if __name__ == '__main__':
    main()
