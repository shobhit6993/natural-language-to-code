class Label(object):
    """Label class for the parser.

    Note that not every `Label` instance needs to have all four attributes
    defined. For example, a description of a Trigger Function will only have
    valid `trigger_channel` and `trigger_fn`; in such cases, the other
    attributes must be set to `None`.
    """

    def __init__(self, trigger_channel=None, trigger_fn=None,
                 action_channel=None, action_fn=None):
        self._trigger_channel = trigger_channel
        """`str` or `None`: Trigger Channel."""
        self._trigger_fn = trigger_fn
        """`str` or `None`: Trigger Function."""
        self._action_channel = action_channel
        """`str` or `None`: Action Channel."""
        self._action_fn = action_fn
        """`str` or `None`: Action Function."""

        # All four attributes cannot be `None`.
        if (self._trigger_channel is None and self._trigger_fn is None and
                    self._action_channel is None and self._action_fn is None):
            raise ValueError

    def __repr__(self):
        return ("Trigger Channel: {}\nTrigger Function: {}\n"
                "Action Channel: {}\nAction Function:{}"
                .format(self._trigger_channel, self._trigger_fn,
                        self._action_channel, self._action_fn))

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    @property
    def trigger_channel(self):
        """`str` or `None`: Trigger Channel."""
        return self._trigger_channel

    @property
    def action_channel(self):
        """`str` or `None`: Action Channel."""
        return self._action_channel

    @property
    def trigger_fn(self):
        """`str` or `None`: Trigger Function combined with Trigger Channel.

        For example, for a Trigger Function "new_photo_post" for Trigger Channel
        "Facebook", the value returned is "Facebook.new_photo_post". This is
        done to differentiate between two Trigger Functions from different
        Trigger Channels with the same keyword.
        """
        return self._trigger_channel + "." + self._trigger_fn

    @property
    def action_fn(self):
        """`str` or `None`: Action Function combined with Action Channel.

        For example, a pure Action Function "upload_to_drive" for the
        Action Channel "Google" is interpreted as "Google.upload_to_drive".
        This is done to differentiate between two Action Functions from
        different Action Channels with the same keyword.
        """
        return self._action_channel + "." + self._action_fn

    @property
    def pure_trigger_fn(self):
        """`str` or `None`: Trigger Function only, without Trigger Channel."""
        return self._trigger_fn

    @property
    def pure_action_fn(self):
        """`str` or `None`: Action Function only, without Action Channel."""
        return self._action_fn
