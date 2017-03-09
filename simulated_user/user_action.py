from enum import Enum


class UserAction:
    """Actions used by the simulated user.

    An action is characterized by its type, and potentially by the predicate
    and its value corresponding to that action. E.g., the action for providing
    the trigger channel slot Facebook would have type as `ActionType.give_slot`,
    predicate set to TRIGGER_CHANNEL, and value set to, say, Facebook.
    Predicate and value may not make sense for certain types of actions.

    Attributes:
        predicate (string): The slot/predicate/variable/placeholder
            corresponding to this action.
        type (ActionType): Action type.
        prev_action (UserAction): Previous action.

    Args:
        predicate (`str`, optional): The slot/predicate/variable/placeholder
            corresponding to this action. Defaults to `None`.
        action_type (ActionType): Action type.
        prev_action (UserAction, optional): Previous action. Defaults to `None`.
    """

    def __init__(self, action_type, predicate=None, prev_action=None):
        self.type = action_type
        self.predicate = predicate
        self.prev_action = prev_action

    def __repr__(self):
        return "Type:{}\nPredicate:{}\nPrevious Action:{}".format(
            self.type, self.predicate, self.prev_action)


class ActionType(Enum):
    free_form = "free_form"
    give_slot = "give_slot"
    affirm = "affirm"
    deny = "deny"
    stop = "stop"
