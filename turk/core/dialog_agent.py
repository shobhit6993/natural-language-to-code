import logging

from dialog.configs import DialogConfiguration
from dialog.dialog_agent import DialogAgent
from dialog.dialog_policy import DialogPolicy
from dialog.dialog_state import DialogState
from dialog.label_description import LabelDescription
from dialog.intention import Intention
from tracker.dialog_tracker import DialogTracker


def create_dialog_agent():
    logging.info("Initializing dialog agent.")
    label_description = LabelDescription()
    intention = Intention
    dialog_policy = DialogPolicy(DialogConfiguration)
    dialog_state = DialogState()
    tracker = DialogTracker()
    dialog_agent = DialogAgent(state=dialog_state, policy=dialog_policy,
                               parser=None, intention=intention,
                               label_description=label_description,
                               istream=None, ostream=None, tracker=tracker)
    return dialog_agent
