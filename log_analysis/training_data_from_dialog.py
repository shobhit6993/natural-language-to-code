"""Generates new training data from dialog in Turk experiment logs."""


from __future__ import absolute_import

import csv
import glob
import logging

from dialog.dialog_action import ActionType
from dialog.constants import Slot, Confirmation, YES_UTTERANCES, NO_UTTERANCES
from log_analysis.log_summary import LogSummary
from log_analysis.argument_parser import arguments_parser_training_data
from log_analysis.sys_utterance_analyzer import SysUtteranceAnalyzer
from simulated_user.label_map import LabelMap
from tracker.constants import DialogStatus


class DialogTrainingSet(object):
    """Extracts and stores new data-points from conversations for the purpose
    of parser retraining.

    Attributes:
        goal (`Goal`): Goal of the dialog, containing recipe details.
        conversation (`Conversation`): The dialog conversation.
    """

    full_datapoints_pos = []
    """:`list` of `dict`: New positive data-points in the format similar to
    that of the IFTTT corpus."""
    t_channel_datapoints_neg = []
    """:`list` of `dict`: New negative data-points for Trigger Channel model."""
    a_channel_datapoints_neg = []
    """:`list` of `dict`: New negative data-points for Action Channel model."""
    t_fn_datapoints_pos = []
    """:`list` of `dict`: New positive data-points for Trigger Fn model."""
    t_fn_datapoints_neg = []
    """:`list` of `dict`: New negative data-points for Trigger Fn model."""
    a_fn_datapoints_pos = []
    """:`list` of `dict`: New positive data-points for Action Fn model."""
    a_fn_datapoints_neg = []
    """:`list` of `dict`: New negative data-points for Action Fn model."""

    _utterance_analyzer = SysUtteranceAnalyzer(LabelMap())

    def __init__(self, goal, conversation):
        """
        Args:
            goal (`Goal`): Goal of the dialog, containing recipe details.
            conversation (`Conversation`): The dialog conversation.
        """
        self.goal = goal
        self.conversation = conversation

        self._free_form_utterance = self.conversation.user_utterances[0]

        self._prev_action = None
        self._prev_slot = None
        self._prev_sys_utterance = None
        self._prev_user_utterance = None

    def construct_training_examples(self):
        """Constructs training examples from the `conversation` between user
        and dialog agent.

        Training examples in the format of original IFTTT dataset -- to train
        all four models on the same description -- as well as training examples
        specific to each model -- for example, a description-trigger function
        pair -- are constructed.

        In case of training examples for specific models, both positive and
        negative training examples might be constructed.
        """
        for sys_utterance, user_utterance in zip(
                self.conversation.sys_utterances,
                self.conversation.user_utterances):
            action = self._system_action(sys_utterance)
            self._parse_utterance_pair(action, sys_utterance, user_utterance)
            if action is not ActionType.reword:
                self._prev_action = action
                self._prev_sys_utterance = sys_utterance
                self._prev_user_utterance = user_utterance

    def _parse_utterance_pair(self, action, sys_utterance, user_utterance):
        t_channel, t_fn, a_channel, a_fn = (
            self.goal.trigger_channel, self.goal.trigger_fn,
            self.goal.action_channel, self.goal.action_fn)

        if action is ActionType.greet:
            self._add_full_datapoint(
                url=self.goal.recipe_url, description=user_utterance,
                trigger_channel=t_channel, action_channel=a_channel,
                trigger_fn=t_fn, action_fn=a_fn,
                datapoints=self.full_datapoints_pos)
        elif action is ActionType.ask_slot:
            slot = self._slot_asked_for(sys_utterance)
            if slot is Slot.trigger_fn:
                self._add_trigger_fn_datapoint(
                    description=user_utterance, trigger_fn=t_fn,
                    trigger_channel=t_channel,
                    datapoints=self.t_fn_datapoints_pos)
            elif slot is Slot.action_fn:
                self._add_action_fn_datapoint(
                    description=user_utterance, action_fn=a_fn,
                    action_channel=a_channel,
                    datapoints=self.a_fn_datapoints_pos)
            else:
                # User utterance containing Channels is parsed using
                # KeywordModel which is not meant to be retrained.
                return
            self._prev_slot = slot
        elif action is ActionType.reword:
            self._parse_utterance_pair(
                action=self._prev_action, user_utterance=user_utterance,
                sys_utterance=self._prev_sys_utterance)
        elif action is ActionType.confirm:
            # If the user is confirming (either by affirmation or denial) a
            # slot, determine which slot, along with its value, is being
            # confirmed by analyzing system-utterance. Training pair, especially
            # a negative one, can be constructed for the inferred slot.
            slot = self._confirmation_for(sys_utterance)
            confirm_response = self._user_confirm_response(user_utterance)
            if slot is Slot.trigger_fn:
                inferred_t_fn = (self._utterance_analyzer.
                                 extract_trigger_fn_from_confirm(sys_utterance,
                                                                 t_channel))

                if inferred_t_fn is None:
                    return

                if (self._prev_action is ActionType.ask_slot and
                        self._prev_slot is Slot.trigger_fn):
                    utterance = self._prev_user_utterance
                else:
                    utterance = self._free_form_utterance

                if confirm_response is Confirmation.yes:
                    # If the user affirms, then their original utterance for
                    # Trigger Function correctly corresponds to the goal
                    # Trigger Function. Data point from this would already have
                    # been obtained. Hence, we don't need to do anything in
                    # this case.
                    pass
                elif confirm_response is Confirmation.no:
                    # If the user denies, then their original utterance for
                    # Trigger Function does not correspond to the Trigger
                    # Function inferred by the dialog agent. A negative data
                    # point can be extracted from this utterance pair
                    self._add_trigger_fn_datapoint(
                        description=utterance, trigger_fn=inferred_t_fn,
                        trigger_channel=t_channel,
                        datapoints=self.t_fn_datapoints_neg)
                else:
                    logging.error("Illegal response to confirmation")
                    raise ValueError
            elif slot is Slot.action_fn:
                inferred_a_fn = (self._utterance_analyzer.
                                 extract_action_fn_from_confirm(sys_utterance,
                                                                a_channel))

                if inferred_a_fn is None:
                    return

                if (self._prev_action is ActionType.ask_slot and
                        self._prev_slot is Slot.action_fn):
                    utterance = self._prev_user_utterance
                else:
                    utterance = self._free_form_utterance

                if confirm_response is Confirmation.yes:
                    # If the user affirms, then their original utterance for
                    # Action Function correctly corresponds to the goal
                    # Action Function. Data point from this would already have
                    # been obtained. Hence, we don't need to do anything in
                    # this case.
                    pass
                elif confirm_response is Confirmation.no:
                    # If the user denies, then their original utterance for
                    # Action Function does not correspond to the Action
                    # Function inferred by the dialog agent. A negative data
                    # point can be extracted from this utterance pair
                    self._add_action_fn_datapoint(
                        description=utterance, action_fn=inferred_a_fn,
                        action_channel=a_channel,
                        datapoints=self.a_fn_datapoints_neg)
                else:
                    logging.error("Illegal response to confirmation")
                    raise ValueError
            elif slot is Slot.trigger_channel:
                if (self._prev_action is ActionType.ask_slot and
                        self._prev_slot is Slot.trigger_channel):
                    # User utterance containing Channels is parsed using
                    # KeywordModel which is not meant to be retrained.
                    return
                utterance = self._free_form_utterance
                inferred_t_channel = self._utterance_analyzer. \
                    extract_trigger_channel_from_confirm(sys_utterance)

                if inferred_t_channel is None:
                    return

                if confirm_response is Confirmation.yes:
                    # If the user affirms, then their free-form utterance
                    # correctly corresponds to the goal Trigger Channel.
                    # Data point from this would already have been obtained.
                    # Hence, we don't need to do anything in this case.
                    pass
                elif confirm_response is Confirmation.no:
                    # If the user denies, then their free-form utterance
                    # does not correspond to the Trigger Channel inferred by
                    # the dialog agent. A negative data point can be extracted
                    # from this utterance pair
                    self._add_trigger_channel_datapoint(
                        description=utterance,
                        trigger_channel=inferred_t_channel,
                        datapoints=self.t_channel_datapoints_neg)
                else:
                    logging.error("Illegal response to confirmation")
                    raise ValueError
            elif slot is Slot.action_channel:
                if (self._prev_action is ActionType.ask_slot and
                        self._prev_slot is Slot.action_channel):
                    # User utterance containing Channels is parsed using
                    # KeywordModel which is not meant to be retrained.
                    return
                utterance = self._free_form_utterance
                inferred_a_channel = self._utterance_analyzer. \
                    extract_action_channel_from_confirm(sys_utterance)

                if inferred_a_channel is None:
                    return

                if confirm_response is Confirmation.yes:
                    # If the user affirms, then their free-form utterance
                    # correctly corresponds to the goal Action Channel.
                    # Data point from this would already have been obtained.
                    # Hence, we don't need to do anything in this case.
                    pass
                elif confirm_response is Confirmation.no:
                    # If the user denies, then their free-form utterance
                    # does not correspond to the Action Channel inferred by
                    # the dialog agent. A negative data point can be extracted
                    # from this utterance pair
                    self._add_action_channel_datapoint(
                        description=utterance,
                        action_channel=inferred_a_channel,
                        datapoints=self.a_channel_datapoints_neg)
                else:
                    logging.error("Illegal response to confirmation")
                    raise ValueError

    @staticmethod
    def _system_action(utterance):
        """Determines the system-action type from its utterance.

         Args:
             utterance (str): Dialog agent's utterance.

         Returns:
             `ActionType`: The system-action type.
         """
        if "Hi! Please describe the" in utterance:
            return ActionType.greet
        elif "Sorry, I didn't get that" in utterance:
            return ActionType.reword
        elif "Which" in utterance or "What" in utterance:
            return ActionType.ask_slot
        elif "Do you want" in utterance:
            return ActionType.confirm
        elif "The applet will" in utterance:
            return ActionType.inform
        elif "Ok" in utterance:
            return ActionType.close
        else:
            raise ValueError

    @staticmethod
    def _slot_asked_for(utterance):
        """Determines the slot being asked for by the dialog agent in its
        utterance corresponding to a `ActionType.ask_slot` request.

        Args:
            utterance (str): Dialog agent's utterance.

        Returns:
            `Slot`: The slot under consideration in the utterance.
        """
        if "Which service should I use to look" in utterance:
            return Slot.trigger_channel
        elif "Which event on" in utterance:
            return Slot.trigger_fn
        elif "Which service should I use to perform" in utterance:
            return Slot.action_channel
        elif "What should I do on" in utterance:
            return Slot.action_fn
        else:
            raise ValueError

    @staticmethod
    def _confirmation_for(utterance):
        """Determines the slot being confirmed by the dialog agent in its
        utterance corresponding to a `ActionType.confirm` request.

        Args:
            utterance (str): Dialog agent's utterance.

        Returns:
            `Slot`: The slot under consideration in the utterance.
        """
        if "Do you want an event on" in utterance:
            return Slot.trigger_channel
        elif "Do you want to trigger" in utterance:
            return Slot.trigger_fn
        elif "Do you want to use" in utterance:
            return Slot.action_channel
        elif "every time the applet is" in utterance:
            return Slot.action_fn
        else:
            raise ValueError

    @staticmethod
    def _user_confirm_response(user_utterance):
        """Determines the type of user response to a confirmation request.

        Args:
            user_utterance (str): User's response to a confirmation request.

        Returns:
            `Confirmation`: Type of user-response to a confirmation request.
        """
        if user_utterance in YES_UTTERANCES:
            return Confirmation.yes
        elif user_utterance in NO_UTTERANCES:
            return Confirmation.no
        else:
            return Confirmation.unknown

    @staticmethod
    def _add_full_datapoint(url, description, trigger_channel,
                            trigger_fn, action_channel, action_fn, datapoints):
        """Constructs a new training data-point in the format similar to that of
        the IFTTT corpus.

        Args:
            url (str): URL of the recipe.
            description (str): Recipe description as provided by the user.
            trigger_channel (str): Actual Trigger Channel of the recipe.
            trigger_fn (str): Actual Trigger Function of the recipe.
            action_channel (str): Actual Action Channel of the recipe.
            action_fn (str): Actual Action Function of the recipe.
            datapoints (`list` of `dict`): The list of data-points to which the
                new data-point should be added.
        """
        datapoint = {'url': url, 'name': description, 'description': '',
                     'trigger_channel': trigger_channel,
                     'trigger_function': trigger_fn,
                     'action_channel': action_channel,
                     'action_function': action_fn}
        datapoints.append(datapoint)

    @staticmethod
    def _add_trigger_fn_datapoint(description, trigger_channel,
                                  trigger_fn, datapoints):
        """Constructs a new training data-point for the Trigger Function model.

        Args:
            description (str): Description of the Trigger Function `trigger_fn`
                as provided by the user.
            trigger_channel (str): Trigger Channel associated with the Trigger
                Function.
            trigger_fn (str): Trigger Function for which the new data-point is
                to be created.
            datapoints (`list` of `dict`): The list of data-points to which the
                new data-point should be added.
        """
        label = trigger_channel + '.' + trigger_fn
        datapoint = {'id': len(datapoints),
                     'description': description, 'label': label}
        datapoints.append(datapoint)

    @staticmethod
    def _add_action_fn_datapoint(description, action_channel, action_fn,
                                 datapoints):
        """Constructs a new training data-point for the Action Function model.

        Args:
            description (str): Description of the Action Function `action_fn`
                as provided by the user.
            action_channel (str): Action Channel associated with the Action
                Function.
            action_fn (str): Action Function for which the new data-point is to
                be created.
            datapoints (`list` of `dict`): The list of data-points to which the
                new data-point should be added.
        """
        label = action_channel + '.' + action_fn
        datapoint = {'id': len(datapoints),
                     'description': description, 'label': label}
        datapoints.append(datapoint)

    @staticmethod
    def _add_trigger_channel_datapoint(description, trigger_channel,
                                       datapoints):
        """Constructs a new training data-point for the Trigger Channel model.

        Args:
            description (str): Description of the Trigger Channel
                `trigger_channel` as provided by the user.
            trigger_channel (str): Trigger Channel for which the new data-point
                is to be created.
            datapoints (`list` of `dict`): The list of data-points to which the
                new data-point should be added.
        """
        datapoint = {'id': len(datapoints),
                     'description': description, 'label': trigger_channel}
        datapoints.append(datapoint)

    @staticmethod
    def _add_action_channel_datapoint(description, action_channel, datapoints):
        """Constructs a new training data-point for the Action Channel model.

        Args:
            description (str): Description of the Action Channel
                `action_channel` as provided by the user.
            action_channel (str): Action Channel for which the new data-point is
                to be created.
            datapoints (`list` of `dict`): The list of data-points to which the
                new data-point should be added.
        """
        datapoint = {'id': len(datapoints),
                     'description': description, 'label': action_channel}
        datapoints.append(datapoint)


def parse_arguments():
    """Parses and logs command-line arguments.

    Returns:
        Namespace: Namespace containing parsed arguments.
    """
    args = arguments_parser_training_data().parse_args()
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


def write_full_datapoints(datapoints, csv_file):
    with open(csv_file, 'w') as f:
        w = csv.DictWriter(
            f, fieldnames=['url', 'name', 'description', 'trigger_channel',
                           'trigger_function', 'action_channel',
                           'action_function'], extrasaction='ignore')
        w.writeheader()
        w.writerows(datapoints)


def write_model_specific_datapoints(datapoints, csv_file):
    with open(csv_file, 'w') as f:
        w = csv.DictWriter(
            f, fieldnames=['id', 'description', 'label'], extrasaction='ignore')
        w.writeheader()
        w.writerows(datapoints)


def main():
    args = parse_arguments()
    log_files = glob.glob(args.log_directories + "/*.log")
    log_summaries = build_log_summaries(log_files)

    for log_summary in log_summaries:
        n = len(log_summary.goals)
        for i in xrange(n):
            # Ignore conversations which were forcefully terminated.
            stats = log_summary.dialog_stats[i]
            if stats.dialog_status_user_view is DialogStatus.terminated:
                logging.info("Ignoring %s because of forced termination.",
                             log_summary.goals[i].recipe_url)
                continue
            if stats.dialog_status_user_view is DialogStatus.failure:
                logging.info("Ignoring %s because of dialog failure.",
                             log_summary.goals[i].recipe_url)
                continue

            goal, conv = log_summary.goals[i], log_summary.conversations[i]
            logging.info("Processing log with recipe: %s", goal.recipe_url)
            dialog_set = DialogTrainingSet(goal, conv)
            dialog_set.construct_training_examples()

    if args.generate_full_pos != "":
        write_full_datapoints(DialogTrainingSet.full_datapoints_pos,
                              args.generate_full_pos)
    if args.generate_t_channel_neg != "":
        write_model_specific_datapoints(
            DialogTrainingSet.t_channel_datapoints_neg,
            args.generate_t_channel_neg)
    if args.generate_a_channel_neg != "":
        write_model_specific_datapoints(
            DialogTrainingSet.a_channel_datapoints_neg,
            args.generate_a_channel_neg)
    if args.generate_t_fn_pos != "":
        write_model_specific_datapoints(DialogTrainingSet.t_fn_datapoints_pos,
                                        args.generate_t_fn_pos)
    if args.generate_t_fn_neg != "":
        write_model_specific_datapoints(DialogTrainingSet.t_fn_datapoints_neg,
                                        args.generate_t_fn_neg)
    if args.generate_a_fn_pos != "":
        write_model_specific_datapoints(DialogTrainingSet.a_fn_datapoints_pos,
                                        args.generate_a_fn_pos)
    if args.generate_a_fn_neg != "":
        write_model_specific_datapoints(DialogTrainingSet.a_fn_datapoints_neg,
                                        args.generate_a_fn_neg)


if __name__ == '__main__':
    main()
