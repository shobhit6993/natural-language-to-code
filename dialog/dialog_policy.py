import logging

from constants import CONF, Confirmation, FUNCTION, ID, Slot
from dialog_action import ActionType, DialogAction


class DialogPolicy:
    """Policy for the dialog agent.

    Attributes:
        config (`configs.DialogConfiguration`): Dialog configuration that
            parametrize dialog policy.

    Args:
        config (`configs.DialogConfiguration`): Dialog configuration that
            parametrize dialog policy.
    """

    def __init__(self, config):
        self.config = config

    def next_action(self, state, prev_action, parse):
        """Computes the next action for the dialog agent.

        The calculation is done according to the policy based on current
        state, previous action, and the parse of the most recent user-utterance.

        Args:
            state (`dialog_state.DialogState`): Current state of dialog agent.
            prev_action (`dialog_action.DialogAction`): The previous
                system-action.
            parse (dict): A dictionary of slot-value pairs representing the
                parse of the current user-utterance.

        Returns:
            `dialog_action.DialogAction`: The next system-action.
        """
        if prev_action is None:
            return self._greet_action()
        elif prev_action.type is ActionType.greet:
            return self._next_action_after_greet(state, prev_action)
        elif prev_action.type is ActionType.ask_slot:
            return self._next_action_after_ask_slot(state, prev_action)
        elif prev_action.type is ActionType.confirm:
            return self._next_action_after_confirm(state, prev_action, parse)
        elif prev_action.type is ActionType.inform:
            return self._next_action_after_inform(state, prev_action, parse)
        else:
            logging.error("%s: Illegal action type %s.",
                          self.next_action.__name__, prev_action)
            raise TypeError

    def _next_action_after_greet(self, state, prev_action):
        # If all four slots have very low confidences, ask the user to reword.
        if self._is_rewording_required(state):
            return self._reword_action(prev_action=prev_action)

        # Determine which of the four slots have confidences above the threshold
        # `self.config.alpha` to not require confirmation. Such slots will be
        # not be explicitly confirmed due to parser's high confidence in their
        # values. Their values are fixed.
        # The slots whose confidences lie between `self.config.alpha` and
        # `self.config.beta` are the ones whose value the parser is not very
        # sure of. Their values are explicitly confirmed before being fixed, or
        # before asking for values of other slots with even lower confidences.

        fixed_predicates, fixed_values = [], []
        # Trigger has preference over Action
        trigger_channel = state.trigger
        if trigger_channel[CONF] < self.config.beta:
            # Confidence is too low. The system should ask the user explicitly
            # for the slot value.
            return self._ask_slot_action(predicate=Slot.trigger_channel)
        elif trigger_channel[CONF] < self.config.alpha:
            # Confidence is low enough to merit a confirmation, but not too low
            # to completely ignore the value and ask for slot again.
            return self._confirm_action(predicate=Slot.trigger_channel,
                                        value=trigger_channel[ID])
        else:
            # Confidence is high enough to not even require a confirmation.
            fixed_predicates.append(Slot.trigger_channel)
            fixed_values.append(trigger_channel[ID])

        # If control reaches here, the Trigger Channel is filled confidently.
        trigger_fn = trigger_channel[FUNCTION]
        if trigger_fn[CONF] < self.config.beta:
            # Confidence is too low. The system should ask the user explicitly
            # for the slot value.
            return self._ask_slot_action(predicate=Slot.trigger_fn)
        elif trigger_fn[CONF] < self.config.alpha:
            # Confidence is low enough to merit a confirmation, but not too low
            # to completely ignore the value and ask for slot again.
            return self._confirm_action(predicate=Slot.trigger_fn,
                                        value=trigger_fn[ID])
        else:
            # Confidence is high enough to not even require a confirmation.
            fixed_predicates.append(Slot.trigger_fn)
            fixed_values.append(trigger_fn[ID])

        # Both Trigger Channel and Trigger Function have sufficient confidence.
        # Proceed to Action.
        action_channel = state.action
        if action_channel[CONF] < self.config.beta:
            # Confidence is too low. The system should ask the user explicitly
            # for the slot value.
            return self._ask_slot_action(predicate=Slot.action_channel)
        elif action_channel[CONF] < self.config.alpha:
            # Confidence is low enough to merit a confirmation, but not too low
            # to completely ignore the value and ask for slot again.
            return self._confirm_action(predicate=Slot.action_channel,
                                        value=action_channel[ID])
        else:
            # Confidence is high enough to not even require a confirmation.
            fixed_predicates.append(Slot.action_channel)
            fixed_values.append(action_channel[ID])

        # If control reaches here, the Action Channel is filled confidently.
        action_fn = action_channel[FUNCTION]
        if action_fn[CONF] < self.config.beta:
            # Confidence is too low. The system should ask the user explicitly
            # for the slot value.
            return self._ask_slot_action(predicate=Slot.action_fn)
        elif action_fn[CONF] < self.config.alpha:
            # Confidence is low enough to merit a confirmation, but not too low
            # to completely ignore the value and ask for slot again.
            return self._confirm_action(predicate=Slot.action_fn,
                                        value=action_fn[ID])
        else:
            # Confidence is high enough to not even require a confirmation.
            fixed_predicates.append(Slot.action_fn)
            fixed_values.append(action_fn[ID])

        # If control reaches here, all four slots have high confidences.
        # The system should inform the user of its interpretation before moving
        # ahead with other slots like Fields. This is not a confirmation action.
        # If the user disagrees, the system will terminate the dialog.
        return self._inform_action(predicate=fixed_predicates,
                                   value=fixed_values)

    def _next_action_after_ask_slot(self, state, prev_action):
        # If the parsed value of slot requested by te system in the last turn
        # has confidence above `self.config.alpha`, it does not need
        # confirmation. We can proceed to request another slot. If the
        # confidence is below `self.config.alpha` but above `self.config.beta`,
        # then it requires an explicit confirmation. Otherwise, the parser is
        # not at all confident about the parse, and the system should ask the
        # user to reword.

        def ask_slot_helper(state_component, slot):
            if state_component[CONF] >= self.config.alpha:
                return self._pick_next_system_action(state)
            elif state_component[CONF] >= self.config.beta:
                return self._confirm_action(predicate=slot,
                                            value=state_component[ID])
            else:
                return self._reword_action(prev_action)

        method_name = self._next_action_after_ask_slot.__name__
        requested_slot = prev_action.predicate
        if requested_slot is Slot.trigger_channel:
            return ask_slot_helper(state.trigger, Slot.trigger_channel)
        elif requested_slot is Slot.trigger_fn:
            return ask_slot_helper(state.trigger[FUNCTION], Slot.trigger_fn)
        elif requested_slot is Slot.action_channel:
            return ask_slot_helper(state.action, Slot.action_channel)
        elif requested_slot is Slot.action_fn:
            return ask_slot_helper(state.action[FUNCTION], Slot.action_fn)
        else:
            logging.error("%s: Illegal slot type %s.", method_name,
                          requested_slot)
            raise TypeError

    def _next_action_after_confirm(self, state, prev_action, parse):
        if parse[Slot.confirmation] is Confirmation.unknown:
            return self._reword_action(prev_action=prev_action)
        elif parse[Slot.confirmation] is Confirmation.no:
            return self._ask_slot_action(predicate=prev_action.predicate)
        elif parse[Slot.confirmation] is Confirmation.yes:
            return self._pick_next_system_action(state)
        else:
            logging.error("%s: Illegal response type %s",
                          self._next_action_after_confirm.__name__,
                          parse[Slot.confirmation])
            raise TypeError

    def _next_action_after_inform(self, state, prev_action, parse):
        if parse[Slot.confirmation] is Confirmation.unknown:
            return self._reword_action(prev_action=prev_action)
        elif parse[Slot.confirmation] is Confirmation.no:
            # Dialog failed.
            return self._close_action()
        elif parse[Slot.confirmation] is Confirmation.yes:
            return self._pick_next_system_action(state, prev_action)
        else:
            logging.error("%s: Illegal response type %s",
                          self._next_action_after_confirm.__name__,
                          parse[Slot.confirmation])
            raise TypeError

    def _pick_next_system_action(self, state, prev_action=None):
        def action_for_slot(state_component, slot):
            if self.config.beta <= state_component[CONF] < self.config.alpha:
                return self._confirm_action(predicate=slot,
                                            value=state_component[ID])
            elif state_component[CONF] < self.config.beta:
                return self._ask_slot_action(predicate=slot)
            else:
                return None

        t_channel_action = action_for_slot(state.trigger, Slot.trigger_channel)
        if t_channel_action is not None:
            return t_channel_action

        t_fn_action = action_for_slot(state.trigger[FUNCTION], Slot.trigger_fn)
        if t_fn_action is not None:
            return t_fn_action

        a_channel_action = action_for_slot(state.action, Slot.action_channel)
        if a_channel_action is not None:
            return a_channel_action

        a_fn_action = action_for_slot(state.action[FUNCTION], Slot.action_fn)
        if a_fn_action is not None:
            return a_fn_action

        # If control reaches here, no slot needs an action. If the previous
        # system-action was `inform`, close the dialog. Otherwise, inform the
        # user of the systems' understanding of the recipe.
        if prev_action is not None and prev_action.type is ActionType.inform:
            return self._close_action()
        else:
            predicates = [Slot.trigger_channel, Slot.trigger_fn,
                          Slot.action_channel, Slot.action_fn]
            values = [state.trigger[ID], state.trigger[FUNCTION][ID],
                      state.action[ID], state.action[FUNCTION][ID]]
            return self._inform_action(predicate=predicates, value=values)

    def _is_rewording_required(self, state):
        # If all four slots have confidences below `self.config.beta`, ask for
        # a rewording.
        return (state.trigger[CONF] < self.config.beta and
                state.trigger[FUNCTION][CONF] < self.config.beta and
                state.action[CONF] < self.config.beta and
                state.action[FUNCTION][CONF] < self.config.beta)

    def _greet_action(self):
        return DialogAction(action_type=ActionType.greet)

    def _reword_action(self, prev_action):
        return DialogAction(
            action_type=ActionType.reword, prev_action=prev_action)

    def _ask_slot_action(self, predicate):
        return DialogAction(
            action_type=ActionType.ask_slot, predicate=predicate)

    def _confirm_action(self, predicate, value):
        return DialogAction(
            action_type=ActionType.confirm, predicate=predicate, value=value)

    def _inform_action(self, predicate, value):
        return DialogAction(
            action_type=ActionType.inform, predicate=predicate, value=value)

    def _close_action(self):
        return DialogAction(action_type=ActionType.close)
