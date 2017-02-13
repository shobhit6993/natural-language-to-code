"""
Evaluate different classes of models together on the same set of test examples
to get the their combined error. For example, trained models of type
`TriggerChannelModel` and `ActionChannelModel` can be tested together to
determine the total error in predicting recipes' channels.
"""

import logging

from combined_model import CombinedModel


def main():
    logging.basicConfig(level=getattr(logging, "INFO"),
                        format='%(levelname)s: %(asctime)s: %(message)s')
    combined_model = CombinedModel(
        use_trigger_channel_model=True, use_action_channel_model=True,
        use_trigger_fn_model=True, use_action_fn_model=True)
    combined_model.test_models()


if __name__ == '__main__':
    main()
