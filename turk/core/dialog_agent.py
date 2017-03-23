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


def get_intent(sys_utterance):
    """Returns the intention behind the system-utterance.

    Args:
        sys_utterance (str): System-utterance.

    Returns:
        str: Intention behind system-utterance.
    """
    if "Hi! Please describe the" in sys_utterance:
        return "open"
    elif ("you want the applet to run" in sys_utterance or
          "Do you want an event on the" in sys_utterance):
        return "trigger_channel"
    elif ("service should cause the applet" in sys_utterance or
          "Do you want to trigger the applet" in sys_utterance):
        return "trigger_function"
    elif ("should I use to perform the desired" in sys_utterance or
          "service to perform the desired action" in sys_utterance):
        return "action_channel"
    elif ("service every time the" in sys_utterance or
          "every time the applet is triggered" in sys_utterance):
        return "action_function"
    elif "Sorry, I didn't get that." in sys_utterance:
        return "reword"
    elif "Is this what you wanted?" in sys_utterance:
        return "inform"
    elif "Ok, bye" in sys_utterance:
        return "close"
