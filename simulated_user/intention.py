class UserIntention(object):
    """Intention, or the goal, of the simulated user while interacting with the
    dialog system.

    The intention of the user is recipe that the user has in mind: It's the
    value of all the slots.

    Attributes:
        recipe_description (str): Description of the recipe.
        trigger_channel (str): Trigger Channel of the recipe.
        trigger_fn (str): Trigger Function of the recipe in dot format
            (e.g. "facebook.upload_new_photo").
        action_channel (str): Action Channel of the recipe.
        action_fn (str): Action Function of the recipe in dot format
            (e.g. "sms.send_a_text_message").

    """

    def __init__(self, recipe_dict):
        """Initializes the values for all the slots that the user needs to
        provide to the dialog system from the recipe defined by the
        `recipe_dict` dictionary.

        Args:
            recipe_dict (dict): The dictionary defining all the attributes of
                the recipe. It must have these keys: "name", "description",
                "trigger_channel", "trigger_function", "action_channel",
                "action_function".
        """
        self.recipe_description = (recipe_dict['name'] + " " +
                                   recipe_dict['description'])
        self.trigger_channel = recipe_dict['trigger_channel']
        self.trigger_fn = (recipe_dict['trigger_channel'] + "." +
                           recipe_dict['trigger_function'])
        self.action_channel = recipe_dict['action_channel']
        self.action_fn = (recipe_dict['action_channel'] + "." +
                          recipe_dict['action_function'])
