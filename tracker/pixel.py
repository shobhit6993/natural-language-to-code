# Collects statistics related to an experiment consisting of multiple dialog
# session.


class Pixel(object):
    """Experiment-level tracker.

    Collects statistics for an a group of dialog-sessions comprising an
    experiment.

    Attributes:
        num_sessions (int): Number of dialog-sessions in the experiment.
        num_successes (int): Number of dialog-sessions that were successful.
        num_failures (int): Number of dialog-sessions that failed.
        num_terminations (int): Number of dialog-sessions that were forcefully
            terminated by users.
        total_length (int): Cumulative length of all dialog sessions.
    """
    def __init__(self):
        self.num_sessions = 0
        self.num_successes = 0
        self.num_failures = 0
        self.num_terminations = 0
        self.total_length = 0

    def __repr__(self):
        return ("Number of sessions={}, Number of successes={}, Number of "
                "failures={}, Number of terminations={}, Total length={}"
                .format(self.num_sessions, self.num_successes,
                        self.num_failures, self.num_terminations,
                        self.total_length))

    def increment_num_sessions(self):
        self.num_sessions += 1

    def increment_num_successes(self):
        self.num_successes += 1

    def increment_num_failures(self):
        self.num_failures += 1

    def increment_num_terminations(self):
        self.num_terminations += 1

    def increment_total_length_by(self, length):
        self.total_length += length
