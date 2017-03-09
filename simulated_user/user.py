import logging

from simulated_user.user_action import ActionType
from dialog.constants import Slot


class SimulatedUser(object):
    """The simulated user.

    Attributes:
        intent (`intention.Intent`): Actual goal of the simulated user.
        policy (`user_policy.UserPolicy`): Policy followed by the simulated user
        label_description (`dialog.label_description.LabelDescription): Mapping
            from labels -- Channels and Functions -- to their descriptions.
        user_utterance (str): The next user utterance.
        slots_provided (list): List of slots already provided to the agent.

    Args:
        intent (`intention.Intent`): Actual goal of the simulated user.
        policy (`user_policy.UserPolicy`): Policy followed by the simulated user
        label_description (`dialog.label_description.LabelDescription): Mapping
            from labels -- Channels and Functions -- to their descriptions.

    """

    def __init__(self, intent, policy, label_description):
        self.intent = intent
        self.policy = policy
        self.label_description = label_description

        self.user_utterance = None
        self.slots_provided = []

    def get(self):
        """Returns user's utterance.

        Returns:
            str: User-utterance.
        """
        # print "USER: " + self.user_utterance
        return self.user_utterance

    def put(self, system_utterance):
        """Reads and outputs the system-utterance.

        Args:
            system_utterance (str): System-utterance.
        """
        # print "SYSTEM: " + system_utterance
        next_action = self.policy.next_action(system_utterance, self.intent)
        if next_action is None:
            return
        self._take_action(next_action)

    def _take_action(self, action):
        """Executes the specified user-action `action`.

        Args:
            action (`user_action.UserAction`): The user-action to be taken.
        """
        if action.type is ActionType.free_form:
            self.user_utterance = self._free_form()
        elif action.type is ActionType.give_slot:
            # If this slot was already provided, force-stop the dialog. This is
            # because the fact that the dialog system requested this slot again
            # shows that it wasn't able to parse the information correctly the
            # last time the simulated user provided that slot. Since the
            # simulated user can only repeat the information word-to-word,
            # there's no point in giving the slot again; it will end in a
            # never-ending dialog.
            if action.predicate in self.slots_provided:
                self.user_utterance = self._stop()
            else:
                self.slots_provided.append(action.predicate)
                self.user_utterance = self._give_slot(action)
        elif action.type is ActionType.affirm:
            self.user_utterance = self._affirm()
        elif action.type is ActionType.deny:
            self.user_utterance = self._deny()
        elif action.type is ActionType.stop:
            self.user_utterance = self._stop()
        else:
            logging.error("%s: Illegal action type in action %s",
                          self._take_action.__name__, action)
            raise TypeError

    def _free_form(self):
        return self.intent.recipe_description

    def _give_slot(self, action):
        slot = action.predicate
        if slot is Slot.trigger_channel:
            channel = self.intent.trigger_channel
            return self.label_description.trigger_channel_description(channel)
        elif slot is Slot.trigger_fn:
            fn = self.intent.trigger_fn
            return self.label_description.trigger_fn_description(fn)
        elif slot is Slot.action_channel:
            channel = self.intent.action_channel
            return self.label_description.action_channel_description(channel)
        elif slot is Slot.action_fn:
            fn = self.intent.action_fn
            return self.label_description.action_fn_description(fn)

    def _affirm(self):
        return "yes"

    def _deny(self):
        return "no"

    def _stop(self):
        return "stop"
