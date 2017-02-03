"""
Dataset class which prepares data for training and evaluation.

This module contains methods needed to load and pre-process dataset or online
inputs.
"""

import csv
import logging
import pickle

from nltk.tokenize import TweetTokenizer
from nltk.stem import SnowballStemmer

from configs import PaperConfiguration
from constants import NULL, NUM_SPECIAL_TOKENS, TurkLabels, UNK, VOCAB_FILE
from constants import DATA_ROOT, TEST_CSV, TRAIN_CSV, TURK_CSV, VALIDATE_CSV
from label import Label
from synthetic_dataset import SyntheticDataset


class Dataset(object):
    """Exposes methods responsible for loading and preparing the dataset for
    training, validation, and testing.

    Attributes:
        config: A configuration class, similar to `configs.PaperConfigurations`.
        path (str): Root directory containing dataset.
        stem (bool): Set to True if the input descriptions should be stemmed.
        vocabulary (dict): Dictionary mapping tokens in the vocabulary to
            integers.
    """

    def __init__(self, stem, config, path=DATA_ROOT):
        self.stem = stem
        self.path = path
        self.vocabulary = {NULL: 0, UNK: 1}
        self.config = config

    def __repr__(self):
        return ("Stem: {}\nPath: {}\nVocabulary: {}"
                .format(str(self.stem), str(self.path), str(self.vocabulary)))

    def load_train(self, vocab_path, use_train_set=True, use_triggers_api=False,
                   use_actions_api=False, use_synthetic_recipes=False,
                   use_names_descriptions=False, load_vocab=False):
        """Loads and pre-processes training data.

        Training data can, potentially, be generated from the actual train set,
        synthetically from API documentation of triggers and actions, and
        synthetic recipes created from their combination.

        Args:
            load_vocab (bool, optional): Load vocabulary from a pickle dump if
                set to `True`. Normally, this would be done during testing.
                During training, it should, normally, be set to `False`.
                Defaults to `False`.
            use_actions_api (bool, optional): Use the Actions API documentation
                to generate train set, if set to `True`. Defaults to `False`.
            use_names_descriptions (bool, optional): Set to `True` if both
                "name" and "description" field of recipes is to be used to
                construct descriptions of recipes. Defaults to `False`.
            use_synthetic_recipes (bool, optional): Use synthetic recipes
                generated by combining all possible Triggers and Actions, if
                set to `True`. Defaults to `False`.
            use_train_set (bool, optional): Use the train set, if set to `True`.
                Defaults to `True`.
            use_triggers_api (bool, optional): Use the Triggers API
                documentation to generate train set, if set to `True`. Defaults
                to `False`.
            vocab_path (str): Path where `self.vocabulary` is dumped or loaded
                from.

        Returns:
            `list` of `str`, `list` of `Label`, `list` of `int`: The first
        entity is the list of descriptions. The second entity is the list
        of corresponding labels. The third entity is the list of lengths
        of descriptions before they were padded (with the maximum length
        being `self.config.sent_len`). The lengths of descriptions which
        were clipped is reported as `self.config.sent_len`.
        """
        descriptions, labels = [], []

        if use_train_set:
            d, l = self._load_dataset(TRAIN_CSV, use_names_descriptions)
            descriptions.extend(d)
            labels.extend(l)

        if use_triggers_api:
            d, l = SyntheticDataset.dataset_from_triggers_api()
            descriptions.extend(d)
            labels.extend(l)

        if use_actions_api:
            d, l = SyntheticDataset.dataset_from_actions_api()
            descriptions.extend(d)
            labels.extend(l)

        if use_synthetic_recipes:
            d, l = SyntheticDataset.dataset_from_synthetic_recipes()
            descriptions.extend(d)
            labels.extend(l)

        inputs = self._tokenize_and_stem(descriptions)
        if load_vocab:
            self.load_vocabulary(vocab_path)
        else:
            self._create_vocabulary(inputs)
            self._dump_vocabulary(vocab_path)
        self.parse_descriptions_with_vocabulary(inputs)
        true_desc_lengths = self.description_lengths_before_padding(inputs)
        self.pad_or_clip(inputs)
        return inputs, labels, true_desc_lengths

    def load_validate(self, use_names_descriptions=False):
        """Loads and pre-processes validation data.

        Args:
            use_names_descriptions (bool, optional): Set to `True` if both
                "name" and "description" field of recipes is to be used to
                construct descriptions of recipes. Defaults to `False`.

        Returns:
            `list` of `str`, `list` of `Label`, `list` of `int`: The first
        entity is the list of descriptions. The second entity is the list
        of corresponding labels. The third entity is the list of lengths
        of descriptions before they were padded (with the maximum length
        being `self.config.sent_len`). The lengths of descriptions which
        were clipped is reported as `self.config.sent_len`.
        """
        descriptions, labels = self._load_dataset(VALIDATE_CSV,
                                                  use_names_descriptions)

        inputs = self._tokenize_and_stem(descriptions)
        self.parse_descriptions_with_vocabulary(inputs)
        true_desc_lengths = self.description_lengths_before_padding(inputs)
        self.pad_or_clip(inputs)
        return inputs, labels, true_desc_lengths

    def load_test(self, use_full_test_set=True, use_english=False,
                  use_english_intelligible=False,
                  use_gold=False, use_names_descriptions=False):
        """Loads and pre-processes testing data.

        The specified subset of test data is loaded. Exactly one of the four
        arguments `use_full_test_set`, `use_use_english`, `use_gold`, and
        `use_use_english_intelligible` must be `True` indicating the desired
        subset to load.

        Args:
            use_names_descriptions (bool, optional): Set to `True` if both
                "name" and "description" field of recipes is to be used to
                construct descriptions of recipes. Defaults to `False`.
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
            `list` of `str`, `list` of `Label`, `list` of `int`: The first
        entity is the list of descriptions. The second entity is the list
        of corresponding labels. The third entity is the list of lengths
        of descriptions before they were padded (with the maximum length
        being `self.config.sent_len`). The lengths of descriptions which
        were clipped is reported as `self.config.sent_len`.

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

        descriptions, labels = self._descriptions_labels(recipes_subset,
                                                         use_names_descriptions)
        inputs = self._tokenize_and_stem(descriptions)
        self.parse_descriptions_with_vocabulary(inputs)
        true_desc_lengths = self.description_lengths_before_padding(inputs)
        self.pad_or_clip(inputs)
        return inputs, labels, true_desc_lengths

    def load_vocabulary(self, vocab_path):
        """Loads vocabulary from the specified pickle dump.

        Args:
            vocab_path (str): Path of the pickle dump.
        """
        logging.debug("Loading vocabulary.")
        with open(vocab_path, 'rb') as f:
            self.vocabulary = pickle.load(f)
        logging.info("Vocabulary loaded.")

    def preprocess_inputs(self, inputs):
        """Pre-processes the input descriptions.

        Args:
            inputs(`list` of `str`): List of recipe descriptions.

        Returns:
            `list` of `str`, `list` of `int`: The first entity is the list of
        descriptions. The second entity is the list of lengths of descriptions
        before they were padded (with the maximum length being
        `self.config.sent_len`). The lengths of descriptions which were clipped
        is reported as `self.config.sent_len`.

        """
        inputs = self._tokenize_and_stem(inputs)
        self.parse_descriptions_with_vocabulary(inputs)
        true_desc_lengths = self.description_lengths_before_padding(inputs)
        self.pad_or_clip(inputs)
        return inputs, true_desc_lengths

    def parse_descriptions_with_vocabulary(self, descriptions):
        """Modifies the descriptions so that it only contains tokens from the
        vocabulary. Other tokens are replaced with the special token `UNK`.
        All tokens are replaced by their corresponding integers.

        Args:
            descriptions (`list` of `list` of `str`): List of descriptions of
                recipes in tokenized form.
        """
        # Make sure that the vocabulary is built.
        assert (len(self.vocabulary) != 0)

        for description in descriptions:
            for i in xrange(len(description)):
                if description[i] not in self.vocabulary:
                    description[i] = self.vocabulary[UNK]
                else:
                    description[i] = self.vocabulary[description[i]]

    def description_lengths_before_padding(self, descriptions):
        """Returns lengths of descriptions before they are padded.

        This list can be used to extract the true lengths of descriptions before
        they are padded. Note that if length of a description is greater than
        `self.config.sent_len`, then its length is reported as
        `self.config.sent_len`.

        Args:
            descriptions (`list` of `list` of `str`): List of descriptions of
                recipes in tokenized form.

        Returns:
            `list` of `int`: Lengths of descriptions.
        """
        return [len(description) if len(description) < self.config.sent_size
                else self.config.sent_size for description in descriptions]

    def pad_or_clip(self, descriptions):
        """Pads or clips descriptions so that they are exactly
        `self.config.sent_len` characters long.

        If number of tokens is less than `self.config.sent_len`, pad `NULL`
        tokens. If number of tokens are greater than `self.config.sent_len`
        use the first `self.config.num_tokens_left` and last
        `self.config.num_tokens_right` tokens.

        Args:
            descriptions (`list` of `list` of `str`): List of descriptions of
                recipes in tokenized form.
        """
        for description in descriptions:
            if len(description) < self.config.sent_size:
                while len(description) < self.config.sent_size:
                    description.append(self.vocabulary[NULL])
            elif len(description) > self.config.sent_size:
                for i in xrange(0, self.config.num_tokens_right):
                    description[i + self.config.num_tokens_left] = \
                        description[i - self.config.num_tokens_right]
                while len(description) > self.config.sent_size:
                    description.pop()

    def _load_dataset(self, filename, use_names_descriptions):
        """Loads description-label pairs from the IFTTT dataset contained in
        the `filename` csv file.

        Args:
            use_names_descriptions (bool): Set to `True` if both "name" and
                "description" field of recipes is to be used to construct
                descriptions of recipes.
            filename (str): Name of csv file from where to read the dataset.

        Returns:
            `list` of `str`, `list` of `Label`: The first entity is the list
        of descriptions. The second entity is the list of corresponding
        labels.
        """
        with open(self.path + filename, 'rb') as f:
            reader = csv.DictReader(f)
            descriptions, labels = self._descriptions_labels(
                reader, use_names_descriptions)

        return descriptions, labels

    def _tokenize_and_stem(self, descriptions):
        """Tokenizes and, optionally, stems the descriptions after converting
        them to lowercase.

        Args:
            descriptions (`list` of `str`): List of descriptions of recipes.

        Returns:
            `list` of `str`: List of stemmed and tokenized descriptions.
        """
        inputs = []
        # Since the descriptions are often in telegraphic language, a tokenizer
        # built for Tweets should work better than one for standard English.
        # Hopefully, the former subsumes the latter in terms of functionality.
        tokenizer = TweetTokenizer()
        if self.stem:
            stemmer = SnowballStemmer("english")

        for description in descriptions:
            # Since TweetTokenizer doesn't tokenize # and @ separately -- they
            # are the special "hashtags" and "mentions" in Tweets -- remove
            # them.
            description = description.replace('#', '').replace('@', '').lower()
            tokenized = tokenizer.tokenize(description)
            if self.stem:
                stemmed = [stemmer.stem(token) for token in tokenized]
                inputs.append(stemmed)
            else:
                inputs.append(tokenized)

        return inputs

    def _create_vocabulary(self, inputs):
        """Creates the vocabulary from recipe descriptions.

        Identify top N most-frequent tokens, and uses them to create the
        vocabulary, where N is `self.config.vocab_size` minus the number of
        special tokens `NUM_SPECIAL_TOKENS`.

        While processing input, these tokens are mapped to themselves; others
        are mapped to the special `UNK` token.

        Args:
            inputs (`list` of `list` of `str`): List of descriptions of recipes
                in tokenized form.
        """
        vocab_size = self.config.vocab_size - NUM_SPECIAL_TOKENS
        token_counts = {}  # Dictionary of tokens and their frequencies.
        for input_ in inputs:
            for token in input_:
                try:
                    token_counts[token] += 1
                except KeyError:
                    # Token not present in the dictionary
                    token_counts[token] = 1

        sorted_tokens = sorted(token_counts.items(),
                               reverse=True, key=lambda (k, v): v)
        num_tokens = len(sorted_tokens)

        i = 0
        while i < num_tokens and i < vocab_size:
            self.vocabulary[sorted_tokens[i][0]] = i + 2
            i += 1

    def _dump_vocabulary(self, vocab_path):
        """Dumps `self.vocabulary` dictionary using pickle.

        Args:
            vocab_path (str): Path where the dump should be saved.
        """
        logging.debug("Dumping vocabulary.")
        with open(vocab_path, 'wb') as f:
            pickle.dump(self.vocabulary, f, protocol=pickle.HIGHEST_PROTOCOL)
        logging.debug("Vocabulary dumped.")

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

    def _descriptions_labels(self, recipes, use_names_descriptions):
        """Extracts descriptions and labels from a list of recipes.

        Given the list of `recipes` dictionary, this method constructs their
        descriptions and the corresponding `Labels` objects off them.

        Args:
            recipes (`DictReader` or `list` of `dict`): List of dictionaries,
                each dictionary representing a recipe with the following keys:
                "url", "trigger_channel", "trigger_function", "action_channel",
                "action_function".:
            use_names_descriptions (bool): Set to `True` if both "name" and
                "description" field of recipes is to be used to construct
                descriptions of recipes.

        Returns:
            `list` of `str`, `list` of `label.Labels`: The first entity is the
            list of descriptions constructed out of `recipes`. The second entity
            is the list of labels for those recipes.
        """
        descriptions, labels = [], []
        for recipe in recipes:
            desc = recipe['name']
            if use_names_descriptions:
                desc += " " + recipe['description']
            descriptions.append(recipe['name'])
            trigger_channel = recipe['trigger_channel']
            trigger_func = recipe['trigger_function']
            action_channel = recipe['action_channel']
            action_func = recipe['action_function']
            label = Label(trigger_channel=trigger_channel,
                          trigger_fn=trigger_func,
                          action_channel=action_channel,
                          action_fn=action_func)
            labels.append(label)
        return descriptions, labels


if __name__ == '__main__':
    dataset = Dataset(stem=True, config=PaperConfiguration)
    inputs, labels = dataset.load_train("./experiments/rnn/dummy/" + VOCAB_FILE)