import csv
import logging


class IftttUtils(object):
    _trigger_fns = {}
    """dict: Maps Trigger Channels to the list of associated Functions."""
    _action_fns = {}
    """dict: Maps Trigger Channels to the list of associated Functions."""

    @classmethod
    def load_ifttt_functions(cls, trigger_fns_csv, action_fns_csv):
        """Loads the list of all Functions available in IFTTT corpus.

        Trigger and Action Functions are loaded and saved separately.

        Args:
            trigger_fns_csv (str): Path of csv file containing Trigger Functions.
            action_fns_csv (str): Path of csv file containing Action Functions.
        """
        with open(trigger_fns_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel, fn = row['label'].split('.')
                try:
                    cls._trigger_fns[channel].append(fn)
                except KeyError:
                    cls._trigger_fns[channel] = [fn]
        logging.info("Loaded Trigger Functions.")

        with open(action_fns_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel, fn = row['label'].split('.')
                try:
                    cls._action_fns[channel].append(fn)
                except KeyError:
                    cls._action_fns[channel] = [fn]
        logging.info("Loaded Action Functions.")

    @classmethod
    def all_trigger_functions(cls, channel):
        """Returns list of Trigger Functions associated to Trigger Channel.

        Args:
            channel (str): Trigger Channel

        Returns:
            list: List of Trigger Functions available for `channel`.
        """
        try:
            return cls._trigger_fns[channel]
        except KeyError:
            logging.error("Invalid Trigger Channel %s", channel)
            raise

    @classmethod
    def all_action_functions(cls, channel):
        """Returns list of Action Functions associated to Action Channel.

        Args:
            channel (str): Action Channel

        Returns:
            list: List of Action Functions available for `channel`.
        """
        try:
            return cls._action_fns[channel]
        except KeyError:
            logging.error("Invalid Action Channel %s", channel)
            raise
