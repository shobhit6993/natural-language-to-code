from dialog.run_pipeline import load_parsers
from dialog.label_description import LabelDescription
from dialog.utterance_parser import UtteranceParser


class Parsers(object):
    t_channel_parser = None
    a_channel_parser = None
    t_fn_parser = None
    a_fn_parser = None
    keyword_parser = None

    utterance_parser = None

    @classmethod
    def load_parsers(cls):
        (t_channel_parser, a_channel_parser, t_fn_parser, a_fn_parser,
         keyword_parser) = load_parsers()
        cls.t_channel_parser = t_channel_parser
        cls.a_channel_parser = a_channel_parser
        cls.t_fn_parser = t_fn_parser
        cls.a_fn_parser = a_fn_parser
        cls.keyword_parser = keyword_parser

        label_description = LabelDescription()
        cls.utterance_parser = UtteranceParser(
            trigger_channel_model=t_channel_parser,
            action_channel_model=a_channel_parser, trigger_fn_model=t_fn_parser,
            action_fn_model=a_fn_parser, keyword_model=keyword_parser,
            label_description=label_description)
