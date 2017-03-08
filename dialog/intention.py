from enum import Enum
import logging

from dialog.constants import Slot
from dialog.dialog_action import ActionType


class Intention(object):
    """Captures the intent of user-utterances so that they can be correctly
    parsed.
    """

    @staticmethod
    def get_intent(system_action, utterance):
        """Returns the intent of user-utterance.

        The intention is determined based on the system-utterance that evoked
        the user's response. The inherent assumption is that the user sticks to
        the flow of the conversation, responding to the questions asked by the
        agent.

        Args:
            system_action (`dialog_action.DialogAction`): The system-action that
                evoked the user's response.
            utterance (str): User-utterance.

        Returns:
            `IntentionType`: Intention of user-utterance.
        """
        if system_action.type is ActionType.greet:
            return IntentionType.free_form
        elif system_action.type is ActionType.reword:
            return Intention.get_intent(system_action.prev_action, utterance)
        elif system_action.type is ActionType.ask_slot:
            if system_action.predicate is Slot.trigger_channel:
                return IntentionType.trigger_channel
            elif system_action.predicate is Slot.trigger_fn:
                return IntentionType.trigger_fn
            elif system_action.predicate is Slot.action_channel:
                return IntentionType.action_channel
            elif system_action.predicate is Slot.action_fn:
                return IntentionType.action_fn
        elif (system_action.type is ActionType.confirm or
                system_action.type is ActionType.inform):
            return IntentionType.confirm
        else:
            logging.error("%s: Illegal action type %s.",
                          Intention.get_intent.__name__, system_action.type)
            raise TypeError


class IntentionType(Enum):
    trigger_channel = "trigger_channel"
    action_channel = "action_channel"
    trigger_fn = "trigger_fn"
    action_fn = "action_fn"
    fields = "fields"
    confirm = "confirm"
    close = "close"
    free_form = "free_form"
