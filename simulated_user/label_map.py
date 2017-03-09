from __future__ import absolute_import

import csv
import logging

from parser.constants import ACTION_CHANNEL_LABELS_PATH, ACTION_FN_LABELS_PATH
from parser.constants import TRIGGER_CHANNEL_LABELS_PATH, TRIGGER_FN_LABELS_PATH


class LabelMap(object):
    """Maintains mapping of description of labels -- Channels and Functions --
    to their ids.
    """

    def __init__(self):
        self._trigger_channels = {}
        """dict: Dictionary mapping Trigger channel names to their ids."""
        self._action_channels = {}
        """dict: Dictionary mapping Action channel names to their ids."""
        self._trigger_fns = {}  # channel_id: {description: func_id}
        """dict: Dictionary mapping Trigger Functions to their ids. Since many
            Channels can have Functions with same descriptions, the dictionary
            maps Channel ids to a dictionary of description-id pairs for the
            Functions specific to that Channel"""
        self._action_fns = {}  # channel_id: {description: func_id}
        """dict: Dictionary mapping Arigger Functions to their ids. Since many
            Channels can have Functions with same descriptions, the dictionary
            maps Channel ids to a dictionary of description-id pairs for the
            Functions specific to that Channel"""

        self.load_description_mapping()

    def load_description_mapping(self):
        """Loads mapping of descriptions of Channels and Functions to their ids.
        """
        with open(TRIGGER_CHANNEL_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._trigger_channels[row['description']] = row['label']

        with open(TRIGGER_FN_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel = row['label'].split('.')[0]
                try:
                    self._trigger_fns[channel][row['description']] = \
                        row['label']
                except KeyError:
                    self._trigger_fns[channel] = \
                        {row['description']: row['label']}

        with open(ACTION_CHANNEL_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._action_channels[row['description']] = row['label']

        with open(ACTION_FN_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel = row['label'].split('.')[0]
                try:
                    self._action_fns[channel][row['description']] = \
                        row['label']
                except KeyError:
                    self._action_fns[channel] = \
                        {row['description']: row['label']}

    def trigger_channel_from_name(self, channel_name):
        """Retrieves Trigger Channel ID from its human-readable name.

        Args:
            channel_name (str): Human-readable name of the Trigger Channel.

        Returns:
            str: Id of the Trigger Channel corresponding to `channel_name`.
        """
        try:
            return self._trigger_channels[channel_name]
        except KeyError:
            logging.error("%s is not a Trigger Channel name.", channel_name)
            raise

    def action_channel_from_name(self, channel_name):
        """Retrieves Action Channel ID from its human-readable name.

        Args:
            channel_name (str): Human-readable name of the Action Channel.

        Returns:
            str: Id of the Action Channel corresponding to `channel_name`.
        """
        try:
            return self._action_channels[channel_name]
        except KeyError:
            logging.error("%s is not an Action Channel name.", channel_name)
            raise

    def trigger_fn_from_description(self, fn_desc, channel):
        """Retrieves Trigger Function ID from its human-readable description.

        Since multiple Trigger Channels can have Functions with the same
        description, `channel`, the id of the Channel of interest, disambiguates
        which one is requested.

        Args:
            fn_desc (str): Human-readable description of Trigger Function.
            channel (str): The id of Trigger Channel which the Function belongs
                to.

        Returns:
            str: Id of the Trigger Function corresponding to `fn_desc`.
        """
        try:
            return self._trigger_fns[channel][fn_desc]
        except KeyError:
            logging.error("%s is not a Trigger Function description.", fn_desc)
            return None

    def action_fn_from_description(self, fn_desc, channel):
        """Retrieves Action Function ID from its human-readable description.

        Since multiple Action Channels can have Functions with the same
        description, `channel`, the id of the Channel of interest, disambiguates
        which one is requested.

        Args:
            fn_desc (str): Human-readable description of Action Function.
            channel (str): The id of Action Channel which the Function belongs
                to.

        Returns:
            str: Id of the Action Function corresponding to `fn_desc`.
        """
        try:
            return self._action_fns[channel][fn_desc]
        except KeyError:
            logging.error("%s is not an Action Function description.", fn_desc)
            return None
