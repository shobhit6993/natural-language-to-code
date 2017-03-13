class ExperimentStatistics(object):
    """Experiment-level statistics, which aggregates multiple log-level
    statistics, such as dialog statistics and survey statistics.

    Attributes:
        num_dialogs (int): Number of dialog sessions in the experiment.
    """

    def __init__(self):
        self.num_dialogs = 0

        self._num_terminated_dialogs = 0
        """:int: Number of dialog sessions that are forcefully terminated by
        users."""
        self._num_incomplete_dialogs = 0
        """int: Number of incomplete dialog sessions."""
        self._num_successful_dialogs_user_view = 0
        """int: Number of dialogs that were successful from user's perspective.
         Success from user's perspective is determined by the last
         user-utterance, in response to system's "inform" utterance."""
        self._num_successful_dialogs_true = 0
        """int: Number of dialogs that were truly successful as determined by
         the agent's final state and the actual goal."""
        self._total_dialog_length = 0
        """:int: Cumulative lengths of all dialogs."""

        self._survey_easy_score = 0.
        self._survey_understand_score = 0.
        self._survey_sensible_score = 0.
        self._survey_long_score = 0.

    @property
    def dialog_length(self):
        """:float: Average dialog length for this experiment."""
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._total_dialog_length / float(self.num_dialogs)

    @property
    def terminated_dialogs(self):
        """:float: Fraction of dialog sessions that are forcefully terminated
        by users."""
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._num_terminated_dialogs / float(self.num_dialogs)

    @property
    def incomplete_dialogs(self):
        """:float: Fraction of incomplete dialog sessions."""
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._num_incomplete_dialogs / float(self.num_dialogs)

    @property
    def successful_dialogs_user_view(self):
        """:float: Fraction of dialogs that were successful from user's
        perspective. Success from user's perspective is determined by the last
        user-utterance, in response to system's "inform" utterance
        """
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._num_successful_dialogs_user_view / float(
                self.num_dialogs)

    @property
    def successful_dialogs_true(self):
        """:float: Fraction of dialogs that were truly successful as determined
        by the agent's final state and the actual goal.
        """
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._num_successful_dialogs_true / float(self.num_dialogs)

    @property
    def survey_easy_score(self):
        """:float: Average score by users for the "easy" survey question."""
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._survey_easy_score / float(self.num_dialogs)

    @property
    def survey_understand_score(self):
        """:float: Average score by users for the understand" survey question.
        """
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._survey_understand_score / float(self.num_dialogs)

    @property
    def survey_sensible_score(self):
        """:float: Average score by users for the "sensible" survey question."""
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._survey_sensible_score / float(self.num_dialogs)

    @property
    def survey_long_score(self):
        """:float: Average score by users for the "long" survey question."""
        if self.num_dialogs == 0:
            return 0.
        else:
            return self._survey_long_score / float(self.num_dialogs)

    def increment_num_terminated_dialogs(self):
        self._num_terminated_dialogs += 1

    def increment_num_dialogs(self):
        self.num_dialogs += 1

    def increment_num_incomplete_dialogs(self):
        self._num_incomplete_dialogs += 1

    def increment_num_successful_dialogs_user_view(self):
        self._num_successful_dialogs_user_view += 1

    def increment_num_successful_dialogs_true(self):
        self._num_successful_dialogs_true += 1

    def increment_total_dialog_length(self, l):
        self._total_dialog_length += l

    def increment_survey_easy_score(self, rating):
        self._survey_easy_score += rating

    def increment_survey_understand_score(self, rating):
        self._survey_understand_score += rating

    def increment_survey_sensible_score(self, rating):
        self._survey_sensible_score += rating

    def increment_survey_long_score(self, rating):
        self._survey_long_score += rating
