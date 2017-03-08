from __future__ import absolute_import

import csv
import logging

from parser.constants import ACTION_CHANNEL_LABELS_PATH, ACTION_FN_LABELS_PATH
from parser.constants import TRIGGER_CHANNEL_LABELS_PATH, TRIGGER_FN_LABELS_PATH


class LabelDescription(object):
    """Mapping from labels -- Channels and Functions -- to their descriptions.
    """
    def __init__(self):
        self._trigger_channels = {}
        """dict: Maps Trigger Channels to their descriptions."""
        self._action_channels = {}
        """dict: Maps Action Channels to their descriptions."""
        self._trigger_fns = {}
        """dict: Maps Trigger Functions to their descriptions."""
        self._action_fns = {}
        """dict: Maps Action Function to their descriptions."""

        self.load_description_templates()

    def load_description_templates(self):
        """Loads descriptions of all labels: Channels and Functions.
        """
        with open(TRIGGER_CHANNEL_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._trigger_channels[row['label']] = row['description']

        with open(TRIGGER_FN_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._trigger_fns[row['label']] = row['description']

        with open(ACTION_CHANNEL_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._action_channels[row['label']] = row['description']

        with open(ACTION_FN_LABELS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._action_fns[row['label']] = row['description']

    def trigger_channel_description(self, channel):
        """Returns the description of a Trigger Channel.

        Args:
            channel (str): Trigger Channel whose description is needed.

        Returns:
            str: Description of the Trigger Channel `channel`.
        """
        if channel == "":
            logging.warn("Trigger Channel is empty.")
            return ""
        try:
            return self._trigger_channels[channel]
        except KeyError:
            logging.error("%s is not a Trigger Channel.", channel)
            raise

    def action_channel_description(self, channel):
        """Returns the description of a Action Channel.

        Args:
            channel (str): Action Channel whose description is needed.

        Returns:
            str: Description of the Action Channel `channel`.
        """
        if channel == "":
            logging.warn("Action Channel is empty.")
            return ""
        try:
            return self._action_channels[channel]
        except KeyError:
            logging.error("%s is not a Action Channel", channel)
            raise

    def trigger_fn_description(self, fn):
        """Returns the description of a Trigger Function.

        Args:
            fn (str): Trigger Function whose description is needed.

        Returns:
            str: Description of the Trigger Function `fn`.
        """
        if fn == "":
            logging.warn("Trigger Function is empty.")
            return ""
        try:
            return self._trigger_fns[fn]
        except KeyError:
            logging.error("%s is not a Trigger Function.", fn)
            raise

    def action_fn_description(self, fn):
        """Returns the description of a Action Function.

        Args:
            fn (str): Action Function whose description is needed.

        Returns:
            str: Description of the Action Function `fn`.
        """
        if fn == "":
            logging.warn("Action Function is empty.")
            return ""
        try:
            return self._action_fns[fn]
        except KeyError:
            logging.error("%s is not a Action Function", fn)
            raise
