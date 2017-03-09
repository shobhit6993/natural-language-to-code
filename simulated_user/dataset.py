"""
Dataset class which loads recipes from test data for the simulated user to
present to the dialog system.
"""

from __future__ import absolute_import

import csv
import logging

from parser.constants import DATA_ROOT, TurkLabels
from parser.constants import TEST_CSV, TURK_CSV, VALIDATE_CSV


class Dataset(object):
    """Exposes methods responsible for loading the dataset for use by the
    simulated user.

    Attributes:
        path (str): Root directory containing dataset.
    """

    def __init__(self, path=DATA_ROOT):
        self.path = path

    def load_validate(self):
        """Loads the validation data.

        Returns:
            `list` of `dict`: The entire set of recipes.
        """
        recipes = []
        with open(self.path + VALIDATE_CSV, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                recipes.append(row)
        return recipes

    def load_test(self, use_full_test_set=True, use_english=False,
                  use_english_intelligible=False, use_gold=False):
        """Loads the testing data.

        The specified subset of test data is loaded. Exactly one of the four
        arguments `use_full_test_set`, `use_use_english`, `use_gold`, and
        `use_use_english_intelligible` must be `True` indicating the desired
        subset to load.

        Args:
            use_gold (bool, optional): Set to `True` if only the gold subset of
                the test set is to be used for testing. Defaults to `False`.
            use_english_intelligible (bool, optional): Set to `True` if only
                that subset of the test set is to be used that is both English
                and intelligible. Defaults to `False`.
            use_english (bool, optional): Set to `True` if only the English
                subset of the test set is to be used for testing.
                Defaults to `False`.
            use_full_test_set (bool, optional): Set to `True` if the complete
                test set is to be used for testing. Defaults to `True`.

        Returns:
            `list` of `dict`: The entire set of recipes.

        """
        # Only one of the four arguments must be True, so that the correct
        # subset can be loaded.
        assert (use_full_test_set + use_english + use_english_intelligible +
                use_gold == 1)

        # First of all, load labels for test recipes obtained from Turk.
        recipes = []
        with open(self.path + TEST_CSV, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                recipes.append(row)
        turk_labels = self._load_turk_labels()

        # Load the requested subset of the test set.
        recipes_subset = []
        if use_full_test_set:
            recipes_subset = self._full_test_set(recipes)
        elif use_english:
            recipes_subset = self._english_subset(recipes, turk_labels)
        elif use_english_intelligible:
            recipes_subset = self._english_intelligible_subset(recipes,
                                                               turk_labels)
        elif use_gold:
            recipes_subset = self._gold_subset(recipes, turk_labels)

        return recipes_subset

    def _load_turk_labels(self):
        """Loads the Turk labels for certain recipes from the csv file.

        Returns:
            dict: Dictionary mapping recipe URLs to list of dictionaries, each
            containing labels for the four attributes. Each dictionary
            contains labels assigned by a Turker.
        """
        logging.debug("Loading turk labels.")
        turk_labels = {}
        with open(self.path + TURK_CSV, "rb") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    turk_labels[row['url']].append(row)
                except KeyError:
                    turk_labels[row['url']] = [row]
        logging.info("Turk labels loaded.")
        return turk_labels

    def _full_test_set(self, recipes):
        """ Returns the full test set.

        Args:
            recipes(`list` of `dict'): List of dictionaries, each dictionary
                representing a recipe with keys the following keys:
                "url", "trigger_channel", "trigger_function", "action_channel",
                "action_function".

        Returns:
            `list` of `dict`: The entire set of recipes.
        """
        return recipes

    def _english_subset(self, recipes, turk_labels):
        """Returns the subset of the test set comprising of English recipes.

        A recipe with any one of the four attributes marked either as
        "nonenglish" or "missing" by at least three Turkers is deemed
        non-English.

        Args:
            turk_labels (dict): Dictionary mapping recipe URLs to list of
                dictionaries, each containing labels for the four attributes.
                Each dictionary contains labels assigned by a Turker.
            recipes (`list` of `dict`): List of dictionaries, each dictionary
                representing a recipe with keys the following keys:
                "url", "trigger_channel", "trigger_function", "action_channel",
                "action_function".

        Returns:
            `list` of `dict`: The English subset of the test set.
        """
        recipes_subset = []
        for recipe in recipes:
            # Check if at least three Turkers labeled at least one field
            # as "nonenglish"
            count = 0
            for turk_label in turk_labels[recipe['url']]:
                condition = (
                    turk_label['trigger_channel'] in TurkLabels.non_english or
                    turk_label['action_channel'] in TurkLabels.non_english or
                    turk_label['trigger_function'] in TurkLabels.non_english or
                    turk_label['action_function'] in TurkLabels.non_english)
                if condition:
                    count += 1
            if count < 3:
                # This recipe is in English.
                recipes_subset.append(recipe)
        return recipes_subset

    def _english_intelligible_subset(self, recipes, turk_labels):
        """Returns the subset of the test set comprising of intelligible,
        English recipes.

        A recipe with any one of the four attributes marked either as
        "nonenglish", "unintelligible", or "missing" by at least three
        Turkers is deemed non-English.

        Args:
            turk_labels (dict): Dictionary mapping recipe URLs to list of
                dictionaries, each containing labels for the four attributes.
                Each dictionary contains labels assigned by a Turker.
            recipes (`list` of `dict`): List of dictionaries, each dictionary
                representing a recipe with keys the following keys:
                "url", "trigger_channel", "trigger_function", "action_channel",
                "action_function".

        Returns:
            `list` of `dict`: The intelligible-and-English subset of test set.
        """
        recipes_subset = []

        for recipe in recipes:
            # Check if at least three Turkers labeled at least one field
            # either as "nonenglish" or "unintelligible"
            count = 0
            for turk_label in turk_labels[recipe['url']]:
                condition = (
                    turk_label[
                        'trigger_channel'] in TurkLabels.unintelligible or
                    turk_label[
                        'action_channel'] in TurkLabels.unintelligible or
                    turk_label[
                        'trigger_function'] in TurkLabels.unintelligible or
                    turk_label['action_function'] in TurkLabels.unintelligible)
                if condition:
                    count += 1
            if count < 3:
                # This recipe is in English and is intelligible.
                recipes_subset.append(recipe)
        return recipes_subset

    def _gold_subset(self, recipes, turk_labels):
        """Returns the gold subset of the test set.

        The gold subset consists of recipes whose labels for all four attributes
        assigned by at least three Turkers match the corresponding true labels.
        The idea is that this is the set of recipes whose descriptions are clean
        and comprehensible, and the original attributes can be guessed by at
        least three Turkers simply by looking at the descriptions.

        Args:
            turk_labels (dict): Dictionary mapping recipe URLs to list of
                dictionaries, each containing labels for the four attributes.
                Each dictionary contains labels assigned by a Turker.
            recipes (`list` of `dict`): List of dictionaries, each dictionary
                representing a recipe with keys the following keys:
                "url", "trigger_channel", "trigger_function", "action_channel",
                "action_function".

        Returns:
            `list` of `dict`: The gold subset of the test set.
        """
        recipes_subset = []
        for recipe in recipes:
            # Check if at least three turkers agree with the true label.
            count = 0
            for turk_label in turk_labels[recipe['url']]:
                condition = (
                    turk_label['trigger_channel'] == recipe[
                        'trigger_channel'] and
                    turk_label['action_channel'] == recipe['action_channel'] and
                    turk_label['trigger_function'] == recipe[
                        'trigger_function'] and
                    turk_label['action_function'] == recipe['action_function'])
                if condition:
                    count += 1
            if count >= 3:
                # This recipe is part of the gold set.
                recipes_subset.append(recipe)
        return recipes_subset
