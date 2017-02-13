import csv

from parser.constants import ACTIONS_PATH, TRIGGERS_PATH
from parser.constants import TRIGGER_CHANNEL_LABELS_PATH, TRIGGER_FN_LABELS_PATH
from parser.constants import ACTION_CHANNEL_LABELS_PATH, ACTION_FN_LABELS_PATH
from parser.label import Label


class SyntheticDataset(object):
    """Exposes methods to generate synthetic dataset from API documentation of
    Trigger Functions and Action Functions.
    """

    @staticmethod
    def dataset_from_triggers_api():
        """Generates a synthetic training dataset from the API documentation
        for Trigger Functions.

        The dataset is creating by parsing and tweaking the natural language
        description of Trigger functions. The descriptions are tweaked using
        hand-built rules so that they conform to a template, form a meaningful
        sentence, and can be directly combined with Action Function
        descriptions to create a synthetic recipe.

        Returns:
            `list` of `str`, `list` of `Label`: The first entity is the list
            of descriptions. The second entity is the list of corresponding
            labels.
        """

        # Get all relevant trigger channels and trigger functions.
        trigger_channels = []
        with open(TRIGGER_CHANNEL_LABELS_PATH, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trigger_channels.append(row['label'])

        trigger_fns = set()
        with open(TRIGGER_FN_LABELS_PATH, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pos = row['label'].find('.')
                channel, fn = row['label'][0:pos], row['label'][pos + 1:]
                trigger_fns.add(channel + "." + fn)

        # Reads Trigger Function descriptions, and extracts phrases -- using
        # hand-built rules -- from the descriptions. These phrases can be
        # directly used as parts of descriptions for synthetic recipes.
        trigger_descs = []
        labels = []
        for filename in trigger_channels:
            with open(TRIGGERS_PATH + "/" + filename + ".csv", 'r') as f:
                reader = csv.DictReader(f)
                for function in reader:
                    function_name = filename + "." + function['id']
                    if function_name not in trigger_fns:
                        # Use only those functions that there in the train set.
                        continue
                    label = Label(trigger_channel=filename,
                                  trigger_fn=function['id'],
                                  action_channel=None,
                                  action_fn=None)
                    description = (function['long_description']
                                   .split('.')[0].lower())
                    if "fires every time" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "every time" till the end of the
                        # first sentence.
                        start = description.find(
                            "fires every time") + len("fires")
                    elif "runs every time" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "every time" till the end of the
                        # first sentence.
                        start = description.find(
                            "runs every time") + len("runs")
                    elif "fires everytime" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "everytime" till the end of the
                        # first sentence.
                        start = description.find(
                            "fires everytime") + len("fires")
                    elif "fire everytime" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "everytime" till the end of the
                        # first sentence.
                        start = description.find(
                            "fire everytime") + len("fire")
                    elif "fire every time" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "every time" till the end of the
                        # first sentence.
                        start = description.find(
                            "fire every time") + len("fire")
                    elif "fire each time" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "each time" till the end of the
                        # first sentence.
                        start = description.find(
                            "fire each time") + len("fire")
                    elif "fires when" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "when" till the end of the
                        # first sentence.
                        start = description.find("fires when") + len("fires")
                    elif "fires if" in description:
                        # In this case, the phrase to be used is the one
                        # starting with "if" till the end of the
                        # first sentence.
                        start = description.find("fires if") + len("fires")
                    elif "fires" in description:
                        # In this case, the phrase to be used is the one
                        # after "fires" till the end of the first sentence.
                        start = description.find("fires") + len("fires")
                    elif "is fired" in description:
                        # In this case, the phrase to be used is the one
                        # after "fired" till the end of the first sentence.
                        start = description.find("is fired") + len("is fired")
                    elif "triggers" in description.lower():
                        # In this case, the phrase to be used is the one
                        # after "triggers" till the end of the first sentence.
                        start = description.find("triggers") + len("triggers")
                    else:
                        # Ignore
                        continue

                    description = description[start:].strip()
                    trigger_descs.append(description)
                    labels.append(label)

        return trigger_descs, labels

    @staticmethod
    def dataset_from_actions_api():
        """Generates a synthetic training dataset from the API documentation
        for Action Functions.

        The dataset is creating by parsing and tweaking the natural language
        description of Action functions. The descriptions are tweaked using
        hand-built rules so that they conform to a template, form a meaningful
        sentence, and can be directly combined with Action Function
        descriptions to create a synthetic recipe.

        Returns:
            `list` of `str`, `list` of `Label`: The first entity is the list
            of descriptions. The second entity is the list of corresponding
            labels.
        """
        # Get all relevant action channels and action functions.
        action_channels = []
        with open(ACTION_CHANNEL_LABELS_PATH, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                action_channels.append(row['label'])

        action_fns = set()
        with open(ACTION_FN_LABELS_PATH, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pos = row['label'].find('.')
                channel, fn = row['label'][0:pos], row['label'][pos + 1:]
                action_fns.add(channel + "." + fn)

        # Reads Action Functions' descriptions, and extracts phrases -- using
        # hand-built rules -- from the descriptions. These phrases can be
        # directly used as parts of descriptions for synthetic recipes.
        action_descs = []
        labels = []
        for filename in action_channels:
            with open(ACTIONS_PATH + "/" + filename + ".csv", 'r') as f:
                reader = csv.DictReader(f)
                for function in reader:
                    function_name = filename + "." + function['id']
                    if function_name not in action_fns:
                        # Use only those functions that there in the train set.
                        continue
                    label = Label(action_channel=filename,
                                  action_fn=function['id'],
                                  trigger_channel=None,
                                  trigger_fn=None)
                    description = (function['long_description']
                                   .split('.')[0].lower())
                    if "this action will" in description:
                        # In this case, the phrase to be used is the one after
                        # "will" till the end of the first sentence.
                        start = (description.find("this action will") +
                                 len("this action will"))
                    elif "the action will" in description:
                        # In this case, the phrase to be used is the one after
                        # "will" till the end of the first sentence.
                        start = (description.find("the action will") +
                                 len("the action will"))
                    elif "this action" in description:
                        # In this case, the phrase to be used is the one after
                        # "Action" till the end of the first sentence.
                        # We can, optionally, remove the 's' from the verb
                        # that follows "Action."
                        start = (description.find("this action") +
                                 len("this action"))
                    elif "this will" in description:
                        # In this case, the phrase to be used is the one after
                        # "will" till the end of the first sentence.
                        start = (description.find("this will") +
                                 len("this will"))
                    else:
                        # If the description does not satisfy any of the
                        # properties above, it is an imperetive description in
                        # itself, and hence, can be directly used as the
                        # description.
                        start = 0

                    description = description[start:].strip()
                    action_descs.append(description)
                    labels.append(label)

        return action_descs, labels

    @staticmethod
    def dataset_from_synthetic_recipes(use_comma=False):
        """Generates a synthetic training recipes by combining the natural
        language descriptions of Trigger Functions and Action Functions given
        in from the API documentation.

        All possible Trigger Functions are paired with all Action Functions to
        generate the synthetic dataset. While it might be the case that not all
        Triggers and Actions are compatible, the corresponding synthetic recipe
        generated by combining such incompatible Triggers and Actions should
        not hurt the model -- if anything, it should aid its training.

        Args:
            use_comma (`bool`, optional): Set of `True` if you want to create
                synthetic recipes whose descriptions are joined by a comma. Note
                that synthetic recipes will always be created with space-joined
                descriptions, irrespective of the value of this argument.
                Defaults to `False`.
        Returns:
            `list` of `str`, `list` of `Label`: The first entity is the list
            of descriptions. The second entity is the list of corresponding
            labels.
        """
        trigger_descs, trigger_labels = \
            SyntheticDataset.dataset_from_triggers_api()
        action_descs, action_labels = \
            SyntheticDataset.dataset_from_actions_api()

        descriptions = []
        labels = []

        for trigger_desc, trigger_label in zip(trigger_descs, trigger_labels):
            for action_desc, action_label in zip(action_descs, action_labels):
                label = Label(action_channel=action_label.action_channel,
                              action_fn=action_label.pure_action_fn,
                              trigger_channel=trigger_label.trigger_channel,
                              trigger_fn=trigger_label.pure_trigger_fn)
                # The two descriptions can be directly combined with a space, or
                # with a comma, either with the trigger description first or the
                # action description first.
                description_1 = trigger_desc + " " + action_desc
                descriptions.append(description_1)
                labels.append(label)

                description_2 = action_desc + " " + trigger_desc
                descriptions.append(description_2)
                labels.append(label)

                if use_comma:
                    description_3 = trigger_desc + ", " + action_desc
                    descriptions.append(description_3)
                    labels.append(label)

                    description_4 = action_desc + ", " + trigger_desc
                    descriptions.append(description_4)
                    labels.append(label)

        return descriptions, labels
