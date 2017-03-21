from __future__ import absolute_import

import logging

from dialog.constants import *
from dialog.dialog_action import ActionType, DialogAction


class DialogAgent:
    """The agent running the dialog system.

    Attributes:
        state (`dialog_state.DialogState`): State of the dialog.
        action (`dialog_action.DialogAction`): Agent's current action.
        policy (`dialog_policy.DialogPolicy`): Policy for the dialog agent.
        parser (`utterance_parser.UtteranceParser`): Parser for user-utterances.
        intention (`intention.Intention`): The intention class.
        label_description (`label_description.LabelDescription`): Maps Channels
            and Functions to their descriptions.
        istream: Any object with a `get` method.
        ostream: Any object with a `get` method.
        tracker (`tracker.dialog_tracker.DialogTracker`): Dialog-level tracking
            that collects statistics for this dialog agent.

    Args:
        state (`dialog_state.DialogState`): State of the dialog.
        policy (`dialog_policy.DialogPolicy`): Policy for the dialog agent.
        parser (`utterance_parser.UtteranceParser`): Parser for
            user-utterances.
        intention (`intention.Intention`): The intention class.
        label_description (`label_description.LabelDescription`): Maps
            Channels and Functions to their descriptions.
        istream: Any object with a `get` method.
        ostream: Any object with a `get` method.
        tracker (`tracker.dialog_tracker.DialogTracker`): Dialog-level
            tracking that collects statistics for this dialog agent.
    """

    def __init__(self, state, policy, parser, intention,
                 label_description, istream, ostream, tracker):
        self.state = state
        self.action = None
        self.policy = policy

        self.parser = parser
        self.intention = intention
        self.label_description = label_description

        self.istream = istream
        self.ostream = ostream

        self.tracker = tracker

    def start_session(self, utterance_parser=None):
        """Starts and maintains dialog session.

        Args:
            utterance_parser (`utterance_parser.UtteranceParser`, optional):
                Parser for user-utterances. Defaults to `None.`. The parser
                used by the agent defaults to `self.parser`, unless it is `None`
                in which case, this one is used. Both cannot be `None`
                simultaneously.
        """
        assert (not (self.parser is None and utterance_parser is None))
        parser = self.parser
        if self.parser is None:
            parser = utterance_parser

        sys_utterance = self.open_dialog()
        self.ostream.put(sys_utterance)
        user_utterance = self._get_user_utterance()

        while True:
            sys_utterance = self.generate_system_response(user_utterance,
                                                          parser)
            self.ostream.put(sys_utterance)
            if self.action.type is ActionType.close:
                break
            user_utterance = self._get_user_utterance()

    def open_dialog(self):
        """Begins a dialog session by having the agent take the first action.

        This method is only responsible for the opening system-utterance. It
        does not carry forward the dialog.

        Returns:
            str: Opening system-utterance.
        """
        self.action = self.policy.next_action(self.state, None, None)
        return self._system_utterance_for_action(self.action)

    def generate_system_response(self, user_utterance, utterance_parser=None):
        """Generates agent's response to the user-utterance.

        Args:
            user_utterance (str): User-utterance.
            utterance_parser (`utterance_parser.UtteranceParser`, optional):
                Parser for user-utterances. Defaults to `None.`. The parser
                used by the agent defaults to `self.parser`, unless it is `None`
                in which case, this one is used. Both cannot be `None`
                simultaneously.

        Returns:
            str: System-utterance.
        """
        assert (not (self.parser is None and utterance_parser is None))

        # Remove trailing full-stops in user-utterance, if present.
        while user_utterance[-1] == '.':
            user_utterance = user_utterance[0:-1]

        parser = self.parser
        if self.parser is None:
            parser = utterance_parser

        if user_utterance.lower().strip() == "stop":
            self.tracker.set_dialog_termination()
            self.action = DialogAction(ActionType.close)
            sys_utterance = self._system_utterance_for_action(self.action)
            return sys_utterance

        intent = self.intention.get_intent(self.action, user_utterance)
        parse = parser.parse_utterance(user_utterance, intent,
                                       self.state)
        self._update_state(self.action, parse)
        self.action = self._next_action(self.action, parse)
        sys_utterance = self._system_utterance_for_action(self.action)

        if self.action.type is ActionType.close:
            if parse[Slot.confirmation] is Confirmation.yes:
                self.tracker.set_dialog_success()
            elif parse[Slot.confirmation] is Confirmation.no:
                self.tracker.set_dialog_failure()
        return sys_utterance

    def _get_user_utterance(self):
        """Reads user utterance.

        Returns:
            str: User-utterance.
        """
        return self.istream.get().strip().lower()

    def _update_state(self, action, parse):
        """Updates dialog state based on agent's previous action and the parse
        of subsequent user-utterance.

        Args:
            action (`dialog_action.DialogAction`): The previous system-action.
            parse (dict): A dictionary of slot-value pairs representing the
                parse of the current user-utterance.
        """
        if action.type is ActionType.greet:
            self._handle_user_initiative(parse)
        elif action.type is ActionType.reword:
            self._handle_rewording(action, parse)
        elif action.type is ActionType.ask_slot:
            self._handle_slot_info(action, parse)
        elif action.type is ActionType.confirm:
            self._handle_confirmation(action, parse)
        elif action.type is ActionType.inform:
            self._handle_inform_response(parse)
        elif action.type is ActionType.close:
            self._handle_close()
        else:
            logging.error("%s: Illegal action type %s.",
                          self._update_state.__name__,
                          action.type)
            raise TypeError

    def _next_action(self, action, parse):
        """Returns next action to be taken by the agent.

        Args:
            action (`dialog_action.DialogAction`): The previous system-action.
            parse (dict): A dictionary of slot-value pairs representing the
                parse of the current user-utterance.

        Returns:
            `dialog_action.DialogAction`: The next system-action.
        """
        if action.type is ActionType.reword:
            action = action.prev_action
        return self.policy.next_action(
            state=self.state, prev_action=action, parse=parse)

    def _handle_user_initiative(self, parse):
        """Updates system-state from the user-utterance corresponding to a
        user-initiative.

        A user-initiative is defined as a user-utterance that is not constrained
        by a previous system-utterance, and is free form. It can include details
        about anything and everything, and such an utterance usually comes at
        at the start of the dialog.

        Args:
            parse (dict): A dictionary of slot-value pairs representing the
                parse of the current user-utterance.
        """
        self.state.update_non_fields_slots(parse)

    def _handle_rewording(self, action, parse):
        """Updates system-state from the user-utterance after a reword request.

        Args:
            action (`dialog_action.DialogAction`): The last system-action that
                evoked the current user-utterance.
            parse (dict): A dictionary of slot-value pairs representing the
                parse of the current user-utterance.
        """
        # The user-utterance after a reword request is the user's response to
        # the system-action right before the reword request. Therefore, this
        # user-utterance can be handled the same way the previous one was
        # handled.
        prev_action = action.prev_action
        if prev_action is None:
            logging.error("%s: Previous action is `None` in action %s",
                          self._handle_rewording.__name__, action)
            raise ValueError
        self._update_state(prev_action, parse)

    def _handle_slot_info(self, action, parse):
        """Updates system-state from the user-utterance after a request for a
        particular slot.

        Args:
            action (`dialog_action.DialogAction`): The last system-action that
                evoked the current user-utterance.
            parse (dict): A dictionary of slot-value pairs representing the
                parse of the current user-utterance.
        """
        self.tracker.increment_slot_request_count()
        # `parse` might contain information for multiple slots, but we'll only
        # consider the information for the slot that the system requested.
        slot_type = action.predicate
        try:
            relevant_parse = {slot_type: parse[slot_type]}
            self.state.update_non_fields_slots(relevant_parse)
        except KeyError:
            logging.error("%s: Missing slot type %s in parse %s.",
                          self._handle_slot_info.__name__, slot_type, parse)
            raise

    def _handle_confirmation(self, action, parse):
        """Updates system-state after the user affirms or denies a confirmation
        of a particular slot.

        Args:
            action (`dialog_action.DialogAction`): The last system-action that
                evoked the current user-utterance.
            parse (dict): A dictionary with `Slot.confirmation` key and one of
                the `enums` of the `Confirmation` class as value
        """
        try:
            self.state.update_from_confirmation(
                slot=action.predicate, value=action.value,
                response=parse[Slot.confirmation])
            if parse[Slot.confirmation] is Confirmation.yes:
                self.tracker.increment_affirm_count()
            elif parse[Slot.confirmation] is Confirmation.no:
                self.tracker.increment_deny_count()
        except KeyError:
            logging.error("%s: Missing key %s in parse %s.",
                          self._handle_confirmation.__name__, Slot.confirmation,
                          parse)
            raise

    def _handle_inform_response(self, parse):
        """Updates system-state after the user affirms or denies the information
        provided by the system.

        The `inform` system-action informs the user of system's current state,
        and expects either an affirmative or denial from the user. This is
        different from `confirm` system-action in that it does not cause any
        state-update: If the user denies the system's state, the dialog ends
        with a failure, otherwise, either the dialog ends with a success or it
        continues to fill remaining slots.

        Args:
            parse (dict): A dictionary with `Slot.confirmation` key and one of
                the `enums` of the `Confirmation` class as value
        """
        # Inform does not require state-update. Only update statistics in the
        # tracker
        if parse[Slot.confirmation] is Confirmation.yes:
            self.tracker.increment_affirm_count()
        elif parse[Slot.confirmation] is Confirmation.no:
            self.tracker.increment_deny_count()

    def _handle_close(self):
        """Closes the dialog. This does not require an update to the state.
        """
        pass

    def _system_utterance_for_action(self, action):
        """Returns the system utterance corresponding to the agent-action.

        Args:
            action (`dialog_action.DialogAction`): The next agent-action.
        Returns:
            str: Next system-utterance.
        """
        if action.type is ActionType.greet:
            return self._greet()
        elif action.type is ActionType.reword:
            return self._reword()
        elif action.type is ActionType.ask_slot:
            return self._ask_slot(action.predicate)
        elif action.type is ActionType.confirm:
            return self._confirm(action)
        elif action.type is ActionType.inform:
            return self._inform(action)
        elif action.type is ActionType.close:
            return self._close()
        else:
            logging.error("%s: Illegal action type in action %s",
                          self._system_utterance_for_action.__name__, action)
            raise TypeError

    def _greet(self):
        self.tracker.increment_dialog_length_by(2)
        return ("Hi! Please describe the applet you want to create for "
                "automating the task you have on your mind.")

    def _reword(self):
        self.tracker.increment_dialog_length_by(2)
        return ("Sorry, I didn't get that. Could you please reword your "
                "previous message?")

    def _ask_slot(self, slot):
        self.tracker.increment_dialog_length_by(2)
        if slot is Slot.trigger_channel:
            message = ("Which service should I use to look for an event when "
                       "you want the applet to run?")
        elif slot is Slot.trigger_fn:
            channel = self.label_description.trigger_channel_description(
                self.state.trigger[ID])
            message = ("Which event on the {} service should I be looking for "
                       "to run the applet?".format(channel))
        elif slot is Slot.action_channel:
            message = ("Which service should I use to perform the desired "
                       "action every time the applet runs?")
        elif slot is Slot.action_fn:
            channel = self.label_description.action_channel_description(
                self.state.action[ID])
            message = ("What should I do on the {} service every time the "
                       "applet runs?".format(channel))
        else:
            logging.error("%s: Illegal slot type %s.",
                          self._ask_slot.__name__, slot)
            raise TypeError
        return message

    def _confirm(self, action):
        self.tracker.increment_dialog_length_by(2)
        if action.predicate is Slot.trigger_channel:
            channel = self.label_description.trigger_channel_description(
                action.value)
            message = ("Do you want an event on the {} service to trigger the "
                       "applet? (yes/no)".format(channel))
        elif action.predicate is Slot.trigger_fn:
            fn = self.label_description.trigger_fn_description(action.value)
            message = ("Do you want to trigger the applet {}? (yes/no)"
                       .format(fn))
        elif action.predicate is Slot.action_channel:
            channel = self.label_description.action_channel_description(
                action.value)
            message = ("Do you want to use the {} service to perform the "
                       "desired action every time the applet is triggered? "
                       "(yes/no)".format(channel))
        elif action.predicate is Slot.action_fn:
            fn = self.label_description.action_fn_description(action.value)
            message = ("Do you want to {} every time the applet is "
                       "triggered? (yes/no)".format(fn))
        else:
            logging.error("%s: Illegal predicate type %s in action %s.",
                          self._confirm.__name__, action.predicate, action)
            raise TypeError
        return message

    def _inform(self, action):
        self.tracker.increment_dialog_length_by(2)
        t_channel = action.value[action.predicate.index(Slot.trigger_channel)]
        t_fn = action.value[action.predicate.index(Slot.trigger_fn)]
        a_channel = action.value[action.predicate.index(Slot.action_channel)]
        a_fn = action.value[action.predicate.index(Slot.action_fn)]

        t_channel = self.label_description.trigger_channel_description(
            t_channel)
        t_fn = self.label_description.trigger_fn_description(t_fn)
        a_channel = self.label_description.action_channel_description(a_channel)
        a_fn = self.label_description.action_fn_description(a_fn)

        message = ("The applet will trigger {}. It will use the {} "
                   "service to look for this event. The action taken will be "
                   "to {}. This action will be performed using the {} "
                   "service. Is this what you wanted? (yes/no)"
                   .format(t_fn, t_channel, a_fn, a_channel))
        return message

    def _close(self):
        self.tracker.increment_dialog_length_by(1)
        return "Ok, bye!"
