import csv
from enum import Enum
import logging
import random
import time

from simulated_user.dataset import Dataset

max_time_diff = 1200


class Recipes(object):
    _recipes = []
    _recipes_status = []

    @classmethod
    def load_recipes_from_test_set(cls, args):
        """Loads the recipes in the test-set of IFTTT corpus based on `args`.

        The `args` define the subset of the test-set to be loaded.

        Args:
            args (`Namespace` or `configs.Configs`): Namespace containing
                parsed arguments, or the `Configs` class where the arguments
                are its class attributes.
        """
        cls._recipes = Dataset().load_test(
            use_full_test_set=args.use_full_test_set,
            use_english=args.use_english,
            use_english_intelligible=args.use_english_intelligible,
            use_gold=args.use_gold)
        cls._add_indices_to_recipes()
        cls._initialize_recipes_status()
        logging.info("Recipes loaded.")

    @classmethod
    def load_recipes_from_file(cls, args):
        """Loads the recipes from csv file specified by `args.recipes_file`.

        Args:
            args (`Namespace` or `configs.Configs`): Namespace containing
                parsed arguments, or the `Configs` class where the arguments
                are its class attributes.
        """
        with open(args.recipes_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls._recipes.append(row)
        cls._add_indices_to_recipes()
        cls._initialize_recipes_status()
        logging.info("Recipes loaded.")

    @classmethod
    def randomly_pick_recipe(cls):
        """Returns a random recipe from the list of `_recipes`.

        Returns:
            dict: A dictionary defining a recipe.
        """
        return random.choice(cls._recipes)

    @classmethod
    def next_recipe(cls):
        curr_time = time.time()
        for index, (status, t) in enumerate(cls._recipes_status):
            # Any unused recipe or a recipe which has been in use for over 30
            # minutes is returned.
            if (status is RecipeStatus.unused or
                    (status is RecipeStatus.in_use and
                     curr_time - t > max_time_diff)):
                cls._recipes_status[index] = (RecipeStatus.in_use, curr_time)
                logging.info("Recipes status: %s", cls._recipes_status)
                return cls._recipes[index]

        # If there are no recipes available, return a random recipe.
        logging.info("All recipes have been used, or are currently in use.")
        return cls.randomly_pick_recipe()

    @classmethod
    def mark_recipe_as_used(cls, index):
        cls._recipes_status[index] = (RecipeStatus.used, time.time())

    @classmethod
    def mark_recipe_as_unused(cls, index):
        cls._recipes_status[index] = (RecipeStatus.unused, time.time())

    @classmethod
    def _initialize_recipes_status(cls):
        curr_time = time.time()
        cls._recipes_status = [(RecipeStatus.unused, curr_time)
                               for _ in cls._recipes]

    @classmethod
    def _add_indices_to_recipes(cls):
        n = len(cls._recipes)
        for i in xrange(n):
            recipe = cls._recipes[i]
            recipe['index'] = i


class RecipeStatus(Enum):
    unused = "unused"
    in_use = "in_use"
    used = "used"
