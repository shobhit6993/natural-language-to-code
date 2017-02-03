UNK = "UKN"  # The special "Unknown" token used to represent OOV-tokens.
NULL = "NULL"  # The special token used to pad inputs.

NUM_SPECIAL_TOKENS = 2

# Number of epochs after which a model is evaluated on validation set.
EVALUATION_FREQ = 1

DATA_ROOT = "./ifttt/data/"  # Root directory where IFTTT dataset resides.
TRAIN_CSV = "train.recipes"  # Name of csv file containing train split.
VALIDATE_CSV = "dev.recipes"  # Name of csv file containing validate split.
TEST_CSV = "test.recipes"  # Name of csv file containing test split.
TURK_CSV = "turk.csv"  # Name of csv file containing Turk labels.

# Directory under which individual csv files for each Trigger Channel reside.
TRIGGERS_PATH = DATA_ROOT + "triggers/relevant/individual"
# Directory under which individual csv files for each Action Channel reside.
ACTIONS_PATH = DATA_ROOT + "actions/relevant/individual"

# Csv file containing mapping from Trigger Functions to ids.
TRIGGER_FN_LABELS_PATH = DATA_ROOT + "label-maps/trigger-functions.csv"
# Csv file containing mapping from Action Functions to ids.
ACTION_FN_LABELS_PATH = DATA_ROOT + "label-maps/action-functions.csv"
# Csv file containing mapping from Trigger Channels to ids.
TRIGGER_CHANNEL_LABELS_PATH = DATA_ROOT + "label-maps/trigger-channels.csv"
# Csv file containing mapping from Action Channels to ids.
ACTION_CHANNEL_LABELS_PATH = DATA_ROOT + "label-maps/action-channels.csv"

STOP_FILE = "./stop"  # File from which "stop" can be read for early stopping.
RNN_EXPT_DIRECTORY = "./experiments/rnn/"  # Experiments directory.
VOCAB_FILE = "vocab.pickle"  # Name of pickle file where vocab is dumped.


class TurkLabels:
    """
    Different categories of labels provided by Amazon Mechanical Turk workers.
    """
    # : list of str: Labels corresponding to recipe descriptions which are not
    # in English.
    non_english = ["nonenglish", "missing"]
    # : list of str: Labels corresponding to recipe descriptions which are
    # either not in English or are unintelligible.
    unintelligible = ["nonenglish", "unintelligible", "missing"]
