import logging

from dialog.constants import Confirmation, Slot, ID
from dialog.constants import NO_UTTERANCES, YES_UTTERANCES
from dialog.intention import IntentionType


class UtteranceParser(object):
    """Parser for user-utterances.

    It is a cocktail of models, each responsible for parsing one aspect of
    user-utterance. In particular, the `UtteranceParser` consists of a model to
        1. parse Trigger Channels from free-form utterances,
        2. parse Trigger Functions from free-form utterances,
        3. parse Action Channels from free-form utterances,
        4. parse Action Functions from free-form utterances, and
        5. parse Channels from user-utterances known to correspond to Channel.

    The utterances are parsed by selecting the appropriate model based on the
    specified "intention" (`intention.IntentionType`) of the utterance.

    Attributes:
        trigger_channel_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Trigger Channels from free-form utterances.
        action_channel_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Action Channels from free-form utterances.
        trigger_fn_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Trigger Functions from free-form utterances.
        action_fn_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Action Functions from free-form utterances.
        keyword_model (`parser.keyword_model.KeywordModel`): Model to parse
            Channels from user-utterances known to correspond to channels. It
            uses flavors of keyword matching.
        label_description(`label_description.LabelDescription`): Mapping from
            labels -- Channels and Functions -- to their descriptions.

    Args:
        trigger_channel_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Trigger Channels from free-form utterances.
        action_channel_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Action Channels from free-form utterances.
        trigger_fn_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Trigger Functions from free-form utterances.
        action_fn_model (`parser.ensembled_model.EnsembledModel`): Model
            to parse Action Functions from free-form utterances.
        keyword_model (`parser.keyword_model.KeywordModel`): Model to parse
            Channels from user-utterances known to correspond to channels. It
            uses flavors of keyword matching.
        label_description (`label_description.LabelDescription`): Mapping from
            labels -- Channels and Functions -- to their descriptions.
    """

    def __init__(self, trigger_channel_model, action_channel_model,
                 trigger_fn_model, action_fn_model, keyword_model,
                 label_description):
        self.trigger_channel_model = trigger_channel_model
        self.action_channel_model = action_channel_model
        self.trigger_fn_model = trigger_fn_model
        self.action_fn_model = action_fn_model

        self.keyword_model = keyword_model
        self.label_description = label_description

    def parse_utterance(self, utterance, intention_type, state):
        """Parses utterance by selecting the right model based on the intention
        `intention_type`.

        Args:
            utterance (str): The user-utterance to be parsed.
            intention_type (`intention.IntentionType`): The intention of the
                utterance `utterance`. The intention helps pick the right model
                to parse the utterance.
            state (`dialog_state.DialogState`): State of dialog agent. The state
                is used to retrieve the Channels that have already been parsed
                to correctly parse Functions: While parsing Functions, the model
                will only consider those Functions that are associated to the
                Channel already fixed in the dialog state.

        Returns:
            dict: Mapping of slots (`constants.Slot`) to parsed values. The
            values are tuples (`str`, `float`) containing parsed label and
            model's confidence in thej parse. The dictionary may contain
            mapping for any (non-empty) subset of slots.
        """
        if intention_type is IntentionType.free_form:
            return self._parse_everything(utterance)
        elif intention_type is IntentionType.trigger_channel:
            # If the dialog agent explicitly asked for the Trigger Channel, the
            # user-utterance is assumed to contain just the name of the
            # Trigger Channel. This utterance can be parsed better by the
            # keyword-based model as compared to the RNN-based model.
            return self._parse_trigger_channel_keyword(utterance)
        elif intention_type is IntentionType.action_channel:
            # If the dialog agent explicitly asked for the Action Channel, the
            # user-utterance is assumed to contain just the name of the
            # Action Channel. This utterance can be parsed better by the
            # keyword-based model as compared to the RNN-based model.
            return self._parse_action_channel_keyword(utterance)
        elif intention_type is IntentionType.trigger_fn:
            channel = state.trigger[ID]
            return self._parse_trigger_fn_based_on_channel(utterance, channel)
        elif intention_type is IntentionType.action_fn:
            channel = state.action[ID]
            return self._parse_action_fn_based_on_channel(utterance, channel)
        elif intention_type is IntentionType.confirm:
            return self._parse_confirmation(utterance)
        else:
            logging.error("%s: Illegal intention type %s.",
                          self.parse_utterance.__name__, intention_type)
            raise TypeError

    def _parse_everything(self, utterance):
        """Assumes the utterance `utterance` to be free-form, and parses values
        for all slots.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of all slots (all `Slot` members) to the respective
            parsed values (each being a `tuple` of `str`, `float`)
            indicating the parsed Channel/Function and model's confidence in
            the parse.
        """
        predictions = {}
        trigger_channel_pred = self._parse_trigger_channel(utterance)
        predictions.update(trigger_channel_pred)

        action_channel_pred = self._parse_action_channel(utterance)
        predictions.update(action_channel_pred)

        trigger_fn_preds = self._parse_trigger_fn(utterance)
        predictions.update(trigger_fn_preds)

        action_fn_preds = self._parse_action_fn(utterance)
        predictions.update(action_fn_preds)

        return predictions

    def _parse_trigger_channel(self, utterance):
        """Parses Trigger Channel from the utterance `utterance`.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of the Trigger Channel slot (`Slot.trigger_channel`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Channel and model's confidence in the parse.
        """
        trigger_channel_preds = self.trigger_channel_model.predict(
            input=utterance, k=1)
        logging.debug("Trigger Channel prediction from RNN: %s",
                      trigger_channel_preds[0])
        return {Slot.trigger_channel: trigger_channel_preds[0]}

    def _parse_action_channel(self, utterance):
        """Parses Action Channel from the utterance `utterance`.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of the Action Channel slot (`Slot.action_channel`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Channel and model's confidence in the parse.
        """
        action_channel_preds = self.action_channel_model.predict(
            input=utterance, k=1)
        logging.debug("Action Channel prediction from RNN: %s",
                      action_channel_preds[0])
        return {Slot.action_channel: action_channel_preds[0]}

    def _parse_trigger_fn(self, utterance):
        """Parses Trigger Function from the utterance `utterance`.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of the Trigger Function slot (`Slot.trigger_fn`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Function and model's confidence in the parse.
        """
        trigger_fn_preds = self.trigger_fn_model.predict(input=utterance, k=0)
        logging.debug("Trigger Function prediction from RNN: %s",
                      trigger_fn_preds[0])
        return {Slot.trigger_fn: trigger_fn_preds[0]}

    def _parse_action_fn(self, utterance):
        """Parses Action Function from the utterance `utterance`.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of the Action Function slot (`Slot.action_fn`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Function and model's confidence in the parse.
        """
        action_fn_preds = self.action_fn_model.predict(input=utterance, k=0)
        logging.debug("Action Function prediction from RNN: %s",
                      action_fn_preds[0])
        return {Slot.action_fn: action_fn_preds[0]}

    def _parse_trigger_fn_based_on_channel(self, utterance, channel):
        """Parses Trigger Function from the utterance `utterance` based on the
        specified Channel `channel`.

        The model is forced to consider only those Functions which are
        associated with the Channel `channel`.

        Args:
            utterance (str): The user-utterance to be parsed.
            channel (str): Trigger Channel in context.

        Returns:
            dict: Mapping of the Trigger Function slot (`Slot.trigger_function`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Function and model's confidence in the parse.
        """
        name = self.label_description.trigger_channel_description(channel)
        utterance = utterance + " on " + name
        preds = self._parse_fn_based_on_channel(self.trigger_fn_model,
                                                utterance, channel)
        logging.debug("Trigger Function prediction from RNN conditioned on "
                      "channel: %s", preds[0])
        return {Slot.trigger_fn: preds[0]}

    def _parse_action_fn_based_on_channel(self, utterance, channel):
        """Parses Action Function from the utterance `utterance` based on the
        specified Channel `channel`.

        The model is forced to consider only those Functions which are
        associated with the Channel `channel`.

        Args:
            utterance (str): The user-utterance to be parsed.
            channel (str): Action Channel in context.

        Returns:
            dict: Mapping of the Action Function slot (`Slot.action_fn`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Function and model's confidence in the parse.
        """
        name = self.label_description.action_channel_description(channel)
        utterance = utterance + " on " + name
        preds = self._parse_fn_based_on_channel(self.action_fn_model,
                                                utterance, channel)
        logging.debug("Action Function prediction from RNN conditioned on "
                      "channel: %s", preds[0])
        return {Slot.action_fn: preds[0]}

    def _parse_fn_based_on_channel(self, model, utterance, channel):
        """Parses Function from the utterance `utterance` based on the
        specified Channel `channel`.

        The model is forced to consider only those Functions which are
        associated with the Channel `channel`.

        Args:
            utterance (str): The user-utterance to be parsed.
            channel (str): Channel in context.

        Returns:
            dict: Mapping of one of the Function slots to the parsed value
            (`tuple` of `str`, `float`) indicating the parsed Function and
            model's confidence in the parse.
        """
        # Get all predictions in reverse sorted order. Among them, consider only
        # the Functions that are compatible with the `channel`.
        # The top-k among them will be returned with their confidences
        # re-weighted so that they sum to 1 among themselves.
        action_fn_preds = model.predict(input=utterance, k=0)
        compatible_preds = self._compatible_predictions(action_fn_preds,
                                                        channel)
        # Recalculate confidences
        confidences = [conf for _, conf in compatible_preds]
        remaining_prob_mass = 1. - sum(confidences)
        new_confidences = []
        for conf in confidences:
            new_confidences.append(
                conf + remaining_prob_mass / len(confidences))

        preds = []
        for i in xrange(len(compatible_preds)):
            preds.append((compatible_preds[i][0], new_confidences[i]))
        return preds

    def _compatible_predictions(self, predictions, desired_channel):
        compatible_preds = []
        for fn, conf in predictions:
            channel = fn.split('.')[0]
            if channel == desired_channel:
                compatible_preds.append((fn, conf))
        return compatible_preds

    def _parse_trigger_channel_keyword(self, utterance):
        """Parses Trigger Channel from the utterance `utterance` using the
        keyword-based model `self.keyword_model`.

        User-utterances that are assumed to contain only the Trigger Channel
        can be parsed better by the keyword-based model as compared to the
        RNN-based model.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of the Trigger Channel slot (`Slot.action_channel`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Channel and model's confidence in the parse.
        """
        trigger_channel_preds = self.keyword_model.predict_trigger_channel(
            input=utterance, k=1)
        logging.debug("Trigger Channel prediction from Keyword model: %s",
                      trigger_channel_preds[0])
        return {Slot.trigger_channel: trigger_channel_preds[0]}

    def _parse_action_channel_keyword(self, utterance):
        """Parses Action Channel from the utterance `utterance` using the
        keyword-based model `self.keyword_model`.

        User-utterances that are assumed to contain only the Action Channel
        can be parsed better by the keyword-based model as compared to the
        RNN-based model.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of the Action Channel slot (`Slot.action_channel`)
            to the parsed value (`tuple` of `str`, `float`) indicating the
            parsed Channel and model's confidence in the parse.
        """
        action_channel_preds = self.keyword_model.predict_action_channel(
            input=utterance, k=1)
        logging.debug("Action Channel prediction from Keyword model: %s",
                      action_channel_preds[0])
        return {Slot.action_channel: action_channel_preds[0]}

    def _parse_confirmation(self, utterance):
        """Parsed the utterance `utterance` assuming it to be a confirmation.

        Args:
            utterance (str): The user-utterance to be parsed.

        Returns:
            dict: Mapping of the confirmation slot (`Slot.confirmation`) to the
            parsed confirmation type (`Confirmation`).
        """
        if utterance in YES_UTTERANCES:
            return {Slot.confirmation: Confirmation.yes}
        elif utterance in NO_UTTERANCES:
            return {Slot.confirmation: Confirmation.no}
        else:
            return {Slot.confirmation: Confirmation.unknown}
