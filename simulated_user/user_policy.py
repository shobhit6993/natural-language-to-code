import logging

from dialog.constants import Slot
from simulated_user.user_action import UserAction, ActionType


class UserPolicy:
    """Policy followed by a simulated user.

    Attributes:
        label_map (`label_map.LabelMap`): Mapping of description of labels
            -- Channels and Functions -- to their ids.

    Args:
        label_map (`label_map.LabelMap`): Mapping of description of labels
            -- Channels and Functions -- to their ids.

    """

    def __init__(self, label_map):
        self.label_map = label_map

    def next_action(self, system_utterance, intent):
        """Computes and returns the next user-action.

        The computation is based on the most recent system-utterance and the
        actual goal of the simulated user.

        Args:
            system_utterance (str): Most recent system-utterance.
            intent (`intention.Intent`): Goal of the simulated user.

        Returns:
            `user_action.UserAction` or `None`: Next action to be taken by the
            simulated user, or `None`.
        """
        if self._system_greet(system_utterance):
            return self._free_form_action()
        elif self._system_reword(system_utterance):
            return self._reword_action()
        elif self._system_ask_slot(system_utterance):
            return self._give_slot_action(system_utterance, intent)
        elif self._system_confirm(system_utterance):
            return self._affirm_or_deny_action(system_utterance, intent)
        elif self._system_inform(system_utterance):
            return self._respond_to_inform(system_utterance, intent)
        else:
            return None

    def _system_greet(self, system_utterance):
        return "Hi! Please describe the" in system_utterance

    def _system_reword(self, system_utterance):
        return "Sorry, I didn't get that" in system_utterance

    def _system_ask_slot(self, system_utterance):
        return "Which" in system_utterance or "What" in system_utterance

    def _system_confirm(self, system_utterance):
        return "Do you want" in system_utterance

    def _system_inform(self, system_utterance):
        return "The applet will" in system_utterance

    def _free_form_action(self):
        return UserAction(ActionType.free_form)

    def _reword_action(self):
        # If the system asks for a rewording, the simulated agent should
        # force-stop the dialog since it cannot really reword its
        # messages: The simulated user will end up using the same message
        # over and over again, thereby making it a non-terminating session.
        return UserAction(ActionType.stop)

    def _give_slot_action(self, sys_utterance, intent):
        if "Which service should I use to look" in sys_utterance:
            # System asked for Trigger Channel.
            return UserAction(ActionType.give_slot,
                              predicate=Slot.trigger_channel)
        elif "Which event on" in sys_utterance:
            # System asked for Trigger Action.
            # Check that the Trigger Channel inferred by the system is
            # consistent with the user's intent. If it's not, force-stop the
            # dialog.
            channel = self._extract_trigger_channel_from_ask_slot(sys_utterance)
            if channel != intent.trigger_channel:
                return UserAction(ActionType.stop)
            return UserAction(ActionType.give_slot, predicate=Slot.trigger_fn)
        elif "Which service should I use to perform" in sys_utterance:
            # System asked for Action Channel.
            return UserAction(ActionType.give_slot,
                              predicate=Slot.action_channel)
        else:
            # System asked for Action Function.
            # Check that the Action Channel inferred by the system is
            # consistent with the user's intent. If it's not, force-stop the
            # dialog.
            channel = self._extract_action_channel_from_ask_slot(sys_utterance)
            if channel != intent.action_channel:
                return UserAction(ActionType.stop)
            return UserAction(ActionType.give_slot, predicate=Slot.action_fn)

    def _affirm_or_deny_action(self, sys_utterance, intent):
        if "Do you want an event on" in sys_utterance:
            channel = self._extract_trigger_channel_from_confirm(sys_utterance)
            if channel == intent.trigger_channel:
                return UserAction(ActionType.affirm)
            else:
                return UserAction(ActionType.deny)
        elif "Do you want to trigger" in sys_utterance:
            fn = self._extract_trigger_fn_from_confirm(sys_utterance,
                                                       intent.trigger_channel)
            if fn == intent.trigger_fn:
                return UserAction(ActionType.affirm)
            else:
                return UserAction(ActionType.deny)
        elif "Do you want to use" in sys_utterance:
            channel = self._extract_action_channel_from_confirm(sys_utterance)
            if channel == intent.action_channel:
                return UserAction(ActionType.affirm)
            else:
                return UserAction(ActionType.deny)
        else:
            fn = self._extract_action_fn_from_confirm(sys_utterance,
                                                      intent.action_channel)
            if fn == intent.action_fn:
                return UserAction(ActionType.affirm)
            else:
                return UserAction(ActionType.deny)

    def _respond_to_inform(self, system_utterance, intent):
        t_channel = self._extract_trigger_channel_from_inform(system_utterance)
        t_fn = self._extract_trigger_fn_from_inform(system_utterance,
                                                    intent.trigger_channel)
        a_channel = self._extract_action_channel_from_inform(system_utterance)
        a_fn = self._extract_action_fn_from_inform(system_utterance,
                                                   intent.action_channel)

        if (t_channel == intent.trigger_channel and
                t_fn == intent.trigger_fn and
                a_channel == intent.action_channel and
                a_fn == intent.action_fn):
            return UserAction(ActionType.affirm)
        else:
            return UserAction(ActionType.deny)

    def _extract_trigger_channel_from_ask_slot(self, utterance):
        start = len("Which event on ")
        end = utterance.index(" should I")
        channel_name = utterance[start:end]
        return self.label_map.trigger_channel_from_name(channel_name)

    def _extract_action_channel_from_ask_slot(self, utterance):
        start = len("What should I do on ")
        end = utterance.index(" every time")
        channel_name = utterance[start:end]
        return self.label_map.action_channel_from_name(channel_name)

    def _extract_trigger_channel_from_confirm(self, utterance):
        start = len("Do you want an event on ")
        end = utterance.index(" service")
        channel_name = utterance[start:end]
        return self.label_map.trigger_channel_from_name(channel_name)

    def _extract_action_channel_from_confirm(self, utterance):
        start = len("Do you want to use ")
        end = utterance.index(" service")
        channel_name = utterance[start:end]
        return self.label_map.action_channel_from_name(channel_name)

    def _extract_trigger_fn_from_confirm(self, utterance, channel):
        start = len("Do you want to trigger the applet ")
        fn_desc = utterance[start:-1]
        return self.label_map.trigger_fn_from_description(fn_desc, channel)

    def _extract_action_fn_from_confirm(self, utterance, channel):
        start = len("Do you want to ")
        end = utterance.index(" every")
        fn_desc = utterance[start:end]
        return self.label_map.action_fn_from_description(fn_desc, channel)

    def _extract_trigger_channel_from_inform(self, utterance):
        start = utterance.index("It will use the ")
        start += len("It will use the ")
        end = utterance.index(" service to look")
        channel_name = utterance[start:end]
        return self.label_map.trigger_channel_from_name(channel_name)

    def _extract_action_channel_from_inform(self, utterance):
        start = utterance.index("performed using the ")
        start += len("performed using the ")
        end = utterance.index(" service.")
        channel_name = utterance[start:end]
        return self.label_map.action_channel_from_name(channel_name)

    def _extract_trigger_fn_from_inform(self, utterance, channel):
        start = len("The applet will trigger ")
        end = utterance.index(". It will")
        fn_desc = utterance[start:end]
        return self.label_map.trigger_fn_from_description(fn_desc, channel)

    def _extract_action_fn_from_inform(self, utterance, channel):
        start = utterance.index("will be to ")
        start += len("will be to ")
        end = utterance.index(". This action")
        fn_desc = utterance[start:end]
        return self.label_map.action_fn_from_description(fn_desc, channel)
