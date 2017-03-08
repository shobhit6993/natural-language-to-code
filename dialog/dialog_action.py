from enum import Enum


class DialogAction:
    """Actions used by the agent.

    An action is characterized by its type, and potentially by the predicate
    and its value corresponding to that action. E.g., the action for confirming
    the trigger channel being Facebook would have type as ActionType.confirm,
    predicate set to TRIGGER_CHANNEL, and value set to Facebook. Predicate and
    value may not make sense for certain types of actions.

    Attributes:
        predicate (str): The slot/predicate/variable/placeholder
            corresponding to this action.
        prev_action (`DialogAction`): The previous action.
        value (str): Value of the predicate.
        type (`ActionType`): Action type.

    Args:
        action_type (`ActionType`): Action type.:
        predicate (str): The slot/predicate/variable/placeholder
            corresponding to this action.:
        value (str): Value of the predicate.:
        prev_action (`DialogAction`): The previous action.
    """

    def __init__(self, action_type, predicate=None, value=None,
                 prev_action=None):
        self.type = action_type
        self.predicate = predicate
        self.value = value
        self.prev_action = prev_action

    def __repr__(self):
        return "Type:{}\nPredicate:{}\nValue:{}\nPrevious Action:{}".format(
            self.type, self.predicate, self.value, self.prev_action)


class ActionType(Enum):
    greet = "greet"
    reword = "reword"
    ask_slot = "ask_slot"
    confirm = "confirm"
    inform = "inform"
    close = "close"
