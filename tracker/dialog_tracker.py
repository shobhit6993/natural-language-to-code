# Collects statistics related to a single dialog session.

from tracker.constants import DialogStatus


class DialogTracker(object):
    """Single-dialog-level tracker.

    Collects statistics about individual dialog sessions

    Attributes:
        dialog_length (int): Length of dialog.
        num_slot_requests (int): Number of slot requests by the agent.
        num_affirms (int): Number of times the user responded with affirmative
            to confirmation requests from the agent.
        num_denies (int): Number of times user denied confirmation requests
            from the agent.
        dialog_status (`constants.dialog_status`): Status of the dialog session.
    """
    def __init__(self):
        self.dialog_length = 0
        self.num_slot_requests = 0
        self.num_affirms = 0
        self.num_denies = 0
        self.dialog_status = None

    def __repr__(self):
        return ("Dialog length={}, Number of slot requests={}, Number of "
                "affirms={}, Number of denies={}, Dialog Status={}"
                .format(self.dialog_length, self.num_slot_requests,
                        self.num_affirms, self.num_denies, self.dialog_status))

    def increment_dialog_length_by(self, length):
        """Increments the dialog-length statistic by the specified number.

        Args:
            length (int): The amount by which to increase the dialog length.
        """
        self.dialog_length += length

    def increment_slot_request_count(self):
        """Increments the number of slot requests by one."""
        self.num_slot_requests += 1

    def increment_affirm_count(self):
        """Increments the affirmative statistic by one."""
        self.num_affirms += 1

    def increment_deny_count(self):
        """Increments the denies statistic by one."""
        self.num_denies += 1

    def set_dialog_failure(self):
        """Sets dialog-status to failed."""
        self.dialog_status = DialogStatus.failure

    def set_dialog_success(self):
        """Sets dialog-status to successful."""
        self.dialog_status = DialogStatus.success

    def set_dialog_termination(self):
        """Sets dialog-status to forced-termination.

        Forced-termination occurs when a user forcefully terminates a dialog
        session prematurely.
        """
        self.dialog_status = DialogStatus.terminated
