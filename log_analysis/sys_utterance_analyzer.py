class SysUtteranceAnalyzer(object):
    """Analyze and extract information from dialog agent's utterances.

    Attributes:
        label_map (`simulate_user.label_map.LabelMap`): Mapping of description
            of labels -- Channels and Functions -- to their ids.

    Args:
        label_map (`simulated_user.label_map.LabelMap`): Mapping of description
            of labels -- Channels and Functions -- to their ids.
    """

    def __init__(self, label_map):
        self.label_map = label_map

    def extract_trigger_channel_from_ask_slot(self, utterance):
        start = len("Which event on ")
        end = utterance.index(" should I")
        channel_name = utterance[start:end]
        return self.label_map.trigger_channel_from_name(channel_name)

    def extract_action_channel_from_ask_slot(self, utterance):
        start = len("What should I do on ")
        end = utterance.index(" every time")
        channel_name = utterance[start:end]
        return self.label_map.action_channel_from_name(channel_name)

    def extract_trigger_channel_from_confirm(self, utterance):
        start = len("Do you want an event on ")
        end = utterance.index(" service")
        channel_name = utterance[start:end]
        return self.label_map.trigger_channel_from_name(channel_name)

    def extract_action_channel_from_confirm(self, utterance):
        start = len("Do you want to use ")
        end = utterance.index(" service")
        channel_name = utterance[start:end]
        return self.label_map.action_channel_from_name(channel_name)

    def extract_trigger_fn_from_confirm(self, utterance, channel):
        start = len("Do you want to trigger the applet ")
        fn_desc = utterance[start:-1]
        return self.label_map.trigger_fn_from_description(fn_desc, channel)

    def extract_action_fn_from_confirm(self, utterance, channel):
        start = len("Do you want to ")
        end = utterance.index(" every")
        fn_desc = utterance[start:end]
        return self.label_map.action_fn_from_description(fn_desc, channel)

    def extract_trigger_channel_from_inform(self, utterance):
        start = utterance.index("It will use the ")
        start += len("It will use the ")
        end = utterance.index(" service to look")
        channel_name = utterance[start:end]
        return self.label_map.trigger_channel_from_name(channel_name)

    def extract_action_channel_from_inform(self, utterance):
        start = utterance.index("performed using the ")
        start += len("performed using the ")
        end = utterance.index(" service.")
        channel_name = utterance[start:end]
        return self.label_map.action_channel_from_name(channel_name)

    def extract_trigger_fn_from_inform(self, utterance, channel):
        start = len("The applet will trigger ")
        end = utterance.index(". It will")
        fn_desc = utterance[start:end]
        return self.label_map.trigger_fn_from_description(fn_desc, channel)

    def extract_action_fn_from_inform(self, utterance, channel):
        start = utterance.index("will be to ")
        start += len("will be to ")
        end = utterance.index(". This action")
        fn_desc = utterance[start:end]
        return self.label_map.action_fn_from_description(fn_desc, channel)
