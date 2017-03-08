import json
import logging

from constants import *
import utils


class DialogState:
    """State of dialog agent.

    Attributes:
        trigger (dict): Slots and values related to Triggers. The structure can
            be found in `state-example.py`.
        action (dict): Slots and values related to Actions. The structure can be
            found in `state-example.py`.
    """

    def __init__(self):
        self.trigger = {}
        self.action = {}

        self._initialize_state()

    def __repr__(self):
        return "IF:\n{}\n\nTHEN:\n{}".format(
            json.dumps(self.trigger, indent=4),
            json.dumps(self.action, indent=4))

    def update_non_fields_slots(self, parse):
        """Updates Trigger- and Action-related slots, except Fields, in the
        state.

        Args:
            parse (dict): Dictionary mapping:
            1. `Slot.trigger_channel` to the Trigger Channel parsed from
            utterance, and/or
            2. `Slot.trigger_fn` to the Trigger Function parsed from
            utterance, and/or
            3. `Slot.action_channel` to the Action Channel parsed from
            utterance, and/or
            4. `Slot.action_fn` to the Action Function parsed from
            utterance.
        """
        if Slot.trigger_channel in parse:
            self.trigger = self._new_channel_entry(parse[Slot.trigger_channel])
        if Slot.trigger_fn in parse:
            self.trigger[FUNCTION] = self._new_function_entry(
                self.trigger, parse[Slot.trigger_fn])
        if Slot.action_channel in parse:
            self.action = self._new_channel_entry(parse[Slot.action_channel])
        if Slot.action_fn in parse:
            self.action[FUNCTION] = self._new_function_entry(
                self.action, parse[Slot.action_fn])

    def update_from_confirmation(self, slot, value, response):
        """Updates state from a confirmation-type user-response.

        Args:
            slot (`constants.Slot`): Slot being confirmed.
            value (str): Value of the slot being confirmed.
            response (`constants.Confirmation`): Type of response: yes or no.
        """
        if response is Confirmation.yes:
            self._update_from_affirm(slot, value)
        elif response is Confirmation.no:
            self._update_from_deny(slot, value)
        elif response is Confirmation.unknown:
            # User neither said yes nor no. Don't update the state.
            pass
        else:
            logging.error("%s: Illegal response type %s",
                          self.update_from_confirmation.__name__, response)
            raise TypeError

    def _initialize_state(self):
        """Initializes state dictionaries."""
        self.trigger = utils.channel_template()
        self.action = utils.channel_template()

    def _new_channel_entry(self, parsed_channel):
        """Returns a new entry for the state using the Channel in
        `parsed_channel`.

        Args:
            parsed_channel (tuple): Tuple containing Channel and the
                associated confidence value.

        Returns:
            dict: New state dictionary with the new Channel.
        """
        new_entry = utils.channel_template()
        new_entry[ID] = parsed_channel[0]
        new_entry[CONF] = parsed_channel[1]
        return new_entry

    def _new_function_entry(self, state_component, parsed_fn):
        """Returns a new entry for the `FUNCTION` part of the state with the
        one of the Functions in `parsed_fn`.

        If the parsed Function is not compatible with the Channel value already
        present in the `state_component`, the parsed Trigger Function is ignored
        and a Function entry with empty `ID` and zero `CONF` is returned.
        This  is because Channels take precedence over Functions, and Channels
        will always be confirmed before Functions, thereby making their values
        in the state more authoritative. Even if their values are not yet
        confirmed, the accuracy of channel-predictor models is higher than that
        of function-predictor models, further justifying this design choice.

        Args:
            state_component (dict): One of the two components of the state, i.e.
                either `self.trigger` or `self.action`.
            parsed_fn (`tuple` of `str`, `float`): Tuple containing Function
                (in dot format, such as "facebook.upload_photo") and the
                associated confidence value.

        Returns:
            dict: New dictionary for the `FUNCTION` slot in state.
        """
        channel, fn = parsed_fn[0].split('.')
        new_entry = utils.functions_template()
        if channel == state_component[ID]:
            new_entry[ID] = parsed_fn[0]
            new_entry[CONF] = parsed_fn[1]
        else:
            new_entry[ID] = ""
            new_entry[CONF] = 0.0
        return new_entry

    def _update_from_affirm(self, slot, value):
        """Updates state from a affirmative response from the user.

        Args:
            slot (`constants.Slot`): Slot being confirmed.
            value (str): Value of the slot being confirmed as correct.
        """
        method_name = self._update_from_affirm.__name__

        def affirm_helper(state_component):
            if state_component[ID] == value:
                state_component[CONF] = 1.0
            else:
                logging.error("%s: Trying to affirm the value %s for slot %s "
                              "which does not exist in state %s.",
                              method_name, value, slot, state_component)

        if slot is Slot.trigger_channel:
            affirm_helper(self.trigger)
        elif slot is Slot.trigger_fn:
            affirm_helper(self.trigger[FUNCTION])
        elif slot is Slot.action_channel:
            affirm_helper(self.action)
        elif slot is Slot.action_fn:
            affirm_helper(self.action[FUNCTION])
        else:
            logging.error("%s: Illegal slot type %s.", method_name, slot)
            raise TypeError

    def _update_from_deny(self, slot, value):
        """Updates state from a denial from the user.

        Args:
            slot (`constants.Slot`): Slot under consideration.
            value (str): Value of the slot being denied.
        """
        method_name = self._update_from_deny.__name__

        def deny_helper(state_component):
            if state_component[ID] == value:
                state_component[ID] = ""
                state_component[CONF] = 0.0
            else:
                logging.error(
                    "%s: Trying to affirm the value %s for slot %s "
                    "which does not exist in state %s.",
                    method_name, value, slot, state_component)

        if slot is Slot.trigger_channel:
            deny_helper(self.trigger)
        elif slot is Slot.trigger_fn:
            deny_helper(self.trigger[FUNCTION])
        elif slot is Slot.action_channel:
            deny_helper(self.action)
        elif slot is Slot.action_fn:
            deny_helper(self.action[FUNCTION])
        else:
            logging.error("%s: Illegal slot type %s.", method_name, slot)
            raise TypeError
