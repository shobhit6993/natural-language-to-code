import logging
import numpy as np

from argument_parser import training_arguments_parser
import configs
from constants import RNN_EXPT_DIRECTORY, ACTION_CHANNEL_LABELS_PATH
from model import Model
import utils


class ActionChannelModel(Model):
    """Model for predicting Action Channels from descriptions.

    """

    def __init__(self, config, path, stem=True):
        super(ActionChannelModel, self).__init__(config, path, stem)

    def _create_label_maps(self):
        """Creates mapping from label keywords to ids by loading the mapping
        from appropriate CSV file.
        """
        self._load_label_maps(ACTION_CHANNEL_LABELS_PATH)
        logging.info("Number of classes = %s", len(self.labels_map))

    def _convert_to_one_hot(self, labels):
        """Converts the label keywords to one-hot vectors.

        For example, a label "dummy" with id 1 is converted to the following
        vector, assuming there are a total of 5 distinct label classes:
        [0,1,0,0,0]

        Args:
            labels (`list` of `label.Label`): Labels.

        Returns:
            numpy.ndarray: 2D array, with rows representing one-hot vector for
            labels.
        """
        indices = []
        for label in labels:
            indices.append(self.labels_map[label.action_channel])

        m, n = len(indices), len(self.labels_map)
        indices = np.array(indices)
        one_hot = np.zeros((m, n))
        one_hot[np.arange(m), indices] = 1.
        return one_hot


def main():
    args = training_arguments_parser().parse_args()

    experiment_name = args.experiment_name[0]
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(levelname)s: %(asctime)s: %(message)s')
    logging.info("Log Level: %s", args.log_level)
    logging.info("Model: %s", args.model[0])
    logging.info("Use Train Set: %s", args.use_train_set)
    logging.info("Use Triggers API: %s", args.use_triggers_api)
    logging.info("Use Actions API: %s", args.use_actions_api)
    logging.info("Use Synthetic Recipes: %s", args.use_synthetic_recipes)
    logging.info("Experiment Name: %s", experiment_name)

    utils.create_experiment_directory(experiment_name)
    path = RNN_EXPT_DIRECTORY + experiment_name + "/"

    if args.model[0] == "ActionChannelModel":
        model = ActionChannelModel(configs.PaperConfiguration, path, True)
        model.load_train_dataset(
            use_train_set=args.use_train_set,
            use_triggers_api=args.use_triggers_api,
            use_actions_api=args.use_actions_api,
            use_synthetic_recipes=args.use_synthetic_recipes,
            use_names_descriptions=True, load_vocab=False)
        model.initialize_network()
        model.train()


if __name__ == '__main__':
    main()
