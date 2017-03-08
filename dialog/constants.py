from enum import Enum

ID = "id"
CONF = "conf"
FUNCTION = "function"
FIELDS = "fields"
VALUE = "value"

# Different affirmative utterances.
YES_UTTERANCES = ["yes", "yep", "yeah", "yea", "yo"]
# Different utterances for denying.
NO_UTTERANCES = ["no", "nope", "nah", "nay"]


class Slot(Enum):
    trigger_channel = "trigger_channel"
    action_channel = "action_channel"
    trigger_fn = "trigger_fn"
    action_fn = "action_fn"
    fields = "fields"
    confirmation = "confirmation"


class Confirmation(Enum):
    yes = "yes"
    no = "no"
    unknown = "unknown"
