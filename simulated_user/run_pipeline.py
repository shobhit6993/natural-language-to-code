# Runs dialog sessions between the dialog agent and a simulated user.


from __future__ import absolute_import

import logging

import dialog.run_pipeline
from dialog.argument_parser import dialog_arguments_parser
from dialog.configs import DialogConfiguration
from dialog.label_description import LabelDescription
from log_analysis.sys_utterance_analyzer import SysUtteranceAnalyzer
from simulated_user.label_map import LabelMap
from simulated_user.dataset import Dataset
from simulated_user.intention import UserIntention
from simulated_user.user import SimulatedUser
from simulated_user.user_policy import UserPolicy
from tracker.pixel import Pixel
from tracker.constants import DialogStatus


def parse_arguments():
    """Parses and logs command-line arguments.

    Returns:
        Namespace: Namespace containing parsed arguments.
    """
    args = dialog_arguments_parser().parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(levelname)s: %(asctime)s: %(message)s')

    assert (args.alpha >= args.beta)
    DialogConfiguration.alpha = args.alpha
    DialogConfiguration.beta = args.beta

    logging.info("Log Level: %s", args.log_level)
    logging.info("Use Full Test Set: %s", args.use_full_test_set)
    logging.info("Use English Subset: %s", args.use_english)
    logging.info("Use English and Intelligible Subset: %s",
                 args.use_english_intelligible)
    logging.info("Use Gold Subset: %s", args.use_gold)
    logging.info("Alpha: %s", args.alpha)
    logging.info("Beta: %s", args.beta)

    return args


def load_test_recipes(args):
    """Loads the recipes in the test-set of IFTTT corpus based on the `args`.

    The `args` define the subset of the test-set to be loaded.

    Args:
        args (Namespace): Namespace containing parsed arguments.

    Returns:
        `list` of `dict`: List of recipes. Each element is a `dict` specifying
        the recipe, containing these keys: "name", "description",
        "trigger_channel", "trigger_function", "action_channel",
        "action_function".
    """
    return Dataset().load_test(
        use_full_test_set=args.use_full_test_set, use_english=args.use_english,
        use_english_intelligible=args.use_english_intelligible,
        use_gold=args.use_gold)


def load_validation_recipes():
    """Loads the recipes in the validation-set of IFTTT corpus.

    Returns:
        `list` of `dict`: List of recipes. Each element is a `dict` specifying
        the recipe, containing these keys: "name", "description",
        "trigger_channel", "trigger_function", "action_channel",
        "action_function".
    """
    return Dataset().load_validate()


def start_session(recipe, trigger_channel_parser, action_channel_parser,
                  trigger_fn_parser, action_fn_parser, keyword_parser):
    """Runs a dialog-session between the dialog agent and a simulated user.

    The simulated user engages in the dialog to describe the recipe described in
    `recipe`.

    Args:
        recipe (dict): The recipe which the simulated user wants to convey.
        trigger_channel_parser (`parser.ensembled_model.EnsembledModel`):
            Model to parse Trigger Channel descriptions.
        action_channel_parser (`parser.ensembled_model.EnsembledModel`):
            Model to parse Action Channel descriptions.
        trigger_fn_parser (`parser.ensembled_model.EnsembledModel`):
            Model to parse Trigger Function descriptions.
        action_fn_parser (`parser.ensembled_model.EnsembledModel`):
            Model to parse Action Function descriptions.
        keyword_parser (`parser.keyword_model.KeywordModel`): Model to parse
            Channels based on keywords.

    Returns:
        tracker.dialog_tracker.DialogTracker: The `DialogTracker` instance
        linked to the dialog agent which contains the metrics related to the
        dialog session.
    """
    logging.info("Starting dialog for recipe %s", recipe)
    user_intention = UserIntention(recipe)
    label_map = LabelMap()
    label_description = LabelDescription()
    sys_utterance_analyzer = SysUtteranceAnalyzer(label_map)
    user_policy = UserPolicy(sys_utterance_analyzer)
    simulated_user = SimulatedUser(user_intention, user_policy,
                                   label_description)
    dialog_agent = dialog.run_pipeline.create_dialog_agent(
        trigger_channel_parser=trigger_channel_parser,
        trigger_fn_parser=trigger_fn_parser,
        action_channel_parser=action_channel_parser,
        action_fn_parser=action_fn_parser, keyword_parser=keyword_parser,
        istream=simulated_user, ostream=simulated_user)
    dialog_agent.start_session()
    return dialog_agent.tracker


def update_statistics(pixel, tracker):
    """Updates experiment-level statistics with the dialog-level statistics.

    Statistics at the level of a single dialog-session, stored in `tracker` are
    used to update the experiment-level statistics, stored in `pixel`, which
    contains multiple dialog sessions.

    Args:
        pixel (`tracker.Pixel`): Experiment-level statistics tracker.
        tracker (tracker.Tracker`): Single dialog-level statistics tracker.
    """
    pixel.increment_num_sessions()
    pixel.increment_total_length_by(tracker.dialog_length)
    if tracker.dialog_status is DialogStatus.success:
        pixel.increment_num_successes()
    elif tracker.dialog_status is DialogStatus.failure:
        pixel.increment_num_failures()
    elif tracker.dialog_status is DialogStatus.terminated:
        pixel.increment_num_terminations()
    else:
        logging.error("Illegal value for the dialog status in tracker %s",
                      tracker)
        raise ValueError


def print_statistics(pixel):
    average_dialog_length = (float(pixel.total_length))/pixel.num_sessions
    logging.info("Number of dialog sessions = %s", pixel.num_sessions)
    print("Number of dialog sessions = %s", pixel.num_sessions)
    logging.info("Average dialog length = %s", average_dialog_length)
    print("Average dialog length = %s", average_dialog_length)

    percent_successful = (100.*pixel.num_successes)/pixel.num_sessions
    percent_failure = (100.*pixel.num_failures)/pixel.num_sessions
    percent_terminated = (100.*pixel.num_terminations)/pixel.num_sessions

    logging.info("Number of successful dialogs = %s", percent_successful)
    print("Number of successful dialogs = %s", percent_successful)
    logging.info("Number of failed dialogs = %s", percent_failure)
    print("Number of failed dialogs = %s", percent_failure)
    logging.info("Number of terminated dialogs = %s", percent_terminated)
    print("Number of terminated dialogs = %s", percent_terminated)

    return average_dialog_length, percent_successful, percent_failure, \
        percent_terminated


def main():
    args = parse_arguments()
    # recipes = load_test_recipes(args)
    recipes = load_validation_recipes()
    t_channel_parser, a_channel_parser, t_fn_parser, a_fn_parser, \
        keyword_parser = dialog.run_pipeline.load_parsers()

    pixel = Pixel()
    for recipe in recipes:
        tracker = start_session(
            recipe=recipe, trigger_channel_parser=t_channel_parser,
            action_channel_parser=a_channel_parser,
            action_fn_parser=a_fn_parser, trigger_fn_parser=t_fn_parser,
            keyword_parser=keyword_parser)
        update_statistics(pixel, tracker)

    return print_statistics(pixel)


if __name__ == '__main__':
    main()
