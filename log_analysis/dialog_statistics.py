class DialogStatistics(object):
    """Individual dialog-session level statistics.

    Attributes:
        dialog_length (int): Length of dialog.
        dialog_status_user_view (`DialogStatus`): Status of the dialog from the
            perspective of the user. This is determined by the last
            user-utterance, in response to system's "inform" utterance.
        dialog_status_true (`DialogStatus`): Actual Status of the dialog based
            on the agent' state and the user's goal.
    """
    def __init__(self):
        self.dialog_length = 0
        self.dialog_status_user_view = None
        self.dialog_status_true = None
