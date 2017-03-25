"""
Performs uncertainty sampling for different classes of models together on the
same set of examples to identify the examples where the models are most
uncertain in any one of the slots. For example, trained models of type
`TriggerChannelModel` and `ActionChannelModel` can be used together to determine
the examples where there is highest uncertainty in predicting recipes' channels.
"""

import logging

from parser.combined_model import CombinedModel


def main():
    logging.basicConfig(level=getattr(logging, "INFO"),
                        format='%(levelname)s: %(asctime)s: %(message)s')
    combined_model = CombinedModel(
        use_trigger_channel_model=True, use_action_channel_model=True,
        use_trigger_fn_model=True, use_action_fn_model=True)
    print combined_model.uncertainty_sampling(0.25, 2)


if __name__ == '__main__':
    main()
