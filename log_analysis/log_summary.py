import logging

from dialog_statistics import DialogStatistics
from dialog.constants import YES_UTTERANCES, NO_UTTERANCES
from tracker.constants import DialogStatus
from .sys_utterance_analyzer import SysUtteranceAnalyzer
from simulated_user.label_map import LabelMap


class LogSummary(object):
    """Summary of the log.

    Note that a log file may have information about multiple user sessions; i.e.
    it may have multiple goals, dialog sessions, and survey responses.

    Attributes:
        goals (`list` of `Goal`): Goals present in the log.
        conversations (`list` of `Conversation`): Dialog sessions in the log.
        surveys (`list` of `Survey`): Survey responses in the log.
        dialog_stats (`list` of `DialogStatistics`): Statics of dialog sessions
            in the log.
    """

    _sys_utterance_analyzer = SysUtteranceAnalyzer(LabelMap())
    """:`SysUtteranceAnalyzer`: Analyze and extract information from
        system-utterances."""

    def __init__(self):
        self.goals = []
        self.conversations = []
        self.surveys = []
        self.dialog_stats = []

    def __repr__(self):
        return ("Goals:{}\nConversations:{}\nSurveys:{}".format(
            self.goals, self.conversations, self.surveys))

    def generate_summary(self, log_file):
        """Generates a summary of the log file.

        Args:
            log_file (str): Path of the log file.

        Returns:
            bool: `True` if everything goes well; if an exception is raised
            due to corrupt log file, `False` is returned.
        """
        with open(log_file, "r") as f:
            try:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if 'recipe_url' in line:
                        self._extract_recipe_data(lines, i)
                    elif '---conversation---' in line:
                        self._extract_conversation(lines, i + 1)
                    elif '---survey---' in line:
                        self._extract_survey(lines, i + 1)
            except (IndexError, ValueError) as e:
                logging.error("Exception %s while parsing log file %s. ",
                              e, log_file)
                # If an exception is raised, the log file might be corrupt.
                # Indicate the caller to discard this log by returning False
                return False
        return True

    def generate_stats(self):
        """Generates statistics about the conversations logged in the log file.
        """
        for goal, conv, _ in zip(self.goals, self.conversations,
                                         self.surveys):
            stats = DialogStatistics()
            stats.dialog_length = (len(conv.sys_utterances) +
                                   len(conv.user_utterances))

            # Set dialog status from the user's perspective -- whether the user
            # considered the dialog a success, indicated by their last utterance
            self._set_dialog_status_user_view(conv.user_utterances[-1], stats)

            # Set the actual dialog status -- whether the agent's state matches
            # the goal of the dialog.
            self._set_dialog_status_true(conv.sys_utterances[-2], goal, stats)
            self.dialog_stats.append(stats)

    def _extract_recipe_data(self, lines, i):
        goal = Goal()

        url_line = lines[i].strip()
        pos = url_line.find(':')
        goal.update_recipe_url(url_line[pos + 1:])

        description_line = lines[i + 1].strip()
        pos = description_line.find(':')
        goal.update_description(description_line[pos + 1:])

        trigger_channel_line = lines[i + 2].strip()
        pos = trigger_channel_line.find(':')
        goal.update_trigger_channel(trigger_channel_line[pos + 1:])

        trigger_function_line = lines[i + 3].strip()
        pos = trigger_function_line.find(':')
        goal.update_trigger_fn(trigger_function_line[pos + 1:])

        action_channel_line = lines[i + 4].strip()
        pos = action_channel_line.find(':')
        goal.update_action_channel(action_channel_line[pos + 1:])

        action_function_line = lines[i + 5].strip()
        pos = action_function_line.find(':')
        goal.update_action_fn(action_function_line[pos + 1:])

        self.goals.append(goal)

    def _extract_conversation(self, lines, start):
        conversation = Conversation()
        for i in xrange(start, len(lines)):
            line = lines[i].strip()
            if '---survey---' in line:
                break
            pos = line.find(':')
            speaker = line[0:pos]
            utterance = line[pos + 1:]
            if speaker == 'ROBOT':
                conversation.add_sys_utterance(utterance)
            elif speaker == 'USER':
                conversation.add_user_utterance(utterance)
            else:
                raise ValueError
        self.conversations.append(conversation)

    def _extract_survey(self, lines, i):
        survey = Survey()
        try:
            easy_line = lines[i].strip()
            pos = easy_line.find(':')
            survey.easy = int(easy_line[pos + 1:])

            understand_line = lines[i + 1].strip()
            pos = understand_line.find(':')
            survey.understand = int(understand_line[pos + 1:])

            sensible_line = lines[i + 2].strip()
            pos = sensible_line.find(':')
            survey.sensible = int(sensible_line[pos + 1:])

            long_line = lines[i + 3].strip()
            pos = long_line.find(':')
            survey.long = int(long_line[pos + 1:])

            comment_line = lines[i + 4].strip()
            pos = comment_line.find(':')
            survey.comment = comment_line[pos + 1:]
        except IndexError:
            survey.taken = False
        else:
            survey.taken = True
        finally:
            self.surveys.append(survey)

    def _set_dialog_status_user_view(self, utterance, stats):
        if utterance in YES_UTTERANCES:
            stats.dialog_status_user_view = DialogStatus.success
        elif utterance in NO_UTTERANCES:
            stats.dialog_status_user_view = DialogStatus.failure
        elif utterance == "stop":
            stats.dialog_status_user_view = DialogStatus.terminated
        else:
            stats.dialog_status_user_view = DialogStatus.incomplete

    def _set_dialog_status_true(self, utterance, goal, stats):
        # This method must be called only after the `dialog_status_user_view`
        # attribute is set.
        assert(stats.dialog_status_user_view is not None)

        # If the conversation either was forcefully stopped by the user or was
        # incomplete, the true dialog status should be same as the dialog status
        # from user's point of view.
        if (stats.dialog_status_user_view is DialogStatus.terminated or
                stats.dialog_status_user_view is DialogStatus.incomplete):
            stats.dialog_status_true = stats.dialog_status_user_view
            return

        # Otherwise, infer the actual dialog status from the system's "inform"
        # utterance
        t_channel, t_fn, a_channel, a_fn = \
            self._extract_channels_fns_from_inform(utterance)

        if (t_channel == goal.trigger_channel and t_fn == goal.trigger_fn and
                a_channel == goal.action_channel and a_fn == goal.action_fn):
            stats.dialog_status_true = DialogStatus.success
        else:
            stats.dialog_status_true = DialogStatus.failure

    def _extract_channels_fns_from_inform(self, utterance):
        """Extracts the Channels and Functions in the agent's state from its
        "inform" utterance.

        Args:
            utterance (str): Agent's second to last utterance, which acts as the
                "inform" utterance.

        Returns:
            `str`, `str`, `str`, `str`: Trigger Channel, Trigger Function (in
            pure form without Channel), Action Channel, and Action Function (in
            pure form without Channel), respectively.
        """
        analyzer = self._sys_utterance_analyzer
        t_channel = analyzer.extract_trigger_channel_from_inform(utterance)
        t_fn = analyzer.extract_trigger_fn_from_inform(utterance, t_channel)
        t_fn = t_fn.split('.')[1]
        a_channel = analyzer.extract_action_channel_from_inform(utterance)
        a_fn = analyzer.extract_action_fn_from_inform(utterance, a_channel)
        a_fn = a_fn.split('.')[1]
        return t_channel, t_fn, a_channel, a_fn


class Goal(object):
    """The true goal of the user scraped from the log.

    The goal is determined by the recipe that the user has on their mind and
    want to convey to the agent through the dialog.

    Attributes:
        recipe_url (str): Recipe's URL.
        description (str): Recipe's short description.
        trigger_channel (str): Recipe's trigger channel.
        trigger_fn (str): Recipe's trigger function in the pure form.
        action_channel (str): Recipe's action channel.
        action_fn (str): Recipe's action function in the pure form.
    """

    def __init__(self):
        self.recipe_url = ""
        self.description = ""
        self.trigger_channel = ""
        self.trigger_fn = ""
        self.action_channel = ""
        self.action_fn = ""

    def __repr__(self):
        return ("URL:{}\nDescription:{}\nTrigger Channel:{}\nTrigger Function:"
                "{}\nAction Channel:{}\nAction Function:{}"
                .format(self.recipe_url, self.description, self.trigger_channel,
                        self.trigger_fn, self.action_channel, self.action_fn))

    def update_trigger_channel(self, channel):
        self.trigger_channel = channel

    def update_action_channel(self, channel):
        self.action_channel = channel

    def update_trigger_fn(self, fn):
        self.trigger_fn = fn

    def update_action_fn(self, fn):
        self.action_fn = fn

    def update_recipe_url(self, url):
        self.recipe_url = url

    def update_description(self, description):
        self.description = description


class Conversation(object):
    """Conversation scraped from the logs.

    Attributes:
        sys_utterances (`list` of `str`): List of system's utterances in the
            order in which they were presented to the user.
        user_utterances (`list` of `str`): List of user's utterances in the
            order in which they were presented to the agent.
    """

    def __init__(self):
        self.sys_utterances = []
        self.user_utterances = []

    def __repr__(self):
        utterances = []
        for sys, user in zip(self.sys_utterances, self.user_utterances):
            utterances.append("ROBOT:{}\nUSER:{}".format(sys, user))
        return '\n'.join(utterances)

    def add_sys_utterance(self, utterance):
        self.sys_utterances.append(utterance)

    def add_user_utterance(self, utterance):
        self.user_utterances.append(utterance)


class Survey(object):
    """Survey responses scraped from the logs.

    Attributes:
        taken (bool): Whether or not the survey data is stored in the log.
        easy (int): User's response to the "easy" question.
        understand (int): User's response to the "understand" question.
        sensible (int): User's response to the "sensible" question.
        long (int): User's response to the "long" question.
        comment (int): User's response to the "comment" question.
    """

    def __init__(self):
        self.taken = False
        self.easy = 0
        self.understand = 0
        self.sensible = 0
        self.long = 0
        self.comment = ""

    def __repr__(self):
        if self.taken:
            return ("Easy={}\nUnderstand={}\nSensible={}\nLong={}\nComment:{}"
                    .format(self.easy, self.understand, self.sensible,
                            self.long, self.comment))
        else:
            return "Not taken."
