from __future__ import unicode_literals

import logging

from django.apps import AppConfig

from core.configs import Configs as args
from core.ifttt_utils import IftttUtils
from core.parsers import Parsers
from core.recipes import Recipes

class TurkConfig(AppConfig):
    name = 'turk'

    def ready(self):
        """Built-in method called by Django while initializing a server. This
        is used to load configurations, parsers, datasets, and recipes when
        the server is launched.
        """
        logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                            format='%(levelname)s: %(asctime)s: %(message)s')
        log_configs(args)
        Parsers.load_parsers()
        Recipes.load_recipes_from_file(args)
        IftttUtils.load_ifttt_functions(args.trigger_fns_csv,
                                        args.action_fns_csv)


def log_configs(args):
    logging.info("Log Level: %s", args.log_level)
    logging.info("Use Full Test Set: %s", args.use_full_test_set)
    logging.info("Use English Subset: %s", args.use_english)
    logging.info("Use English and Intelligible Subset: %s",
                 args.use_english_intelligible)
    logging.info("Use Gold Subset: %s", args.use_gold)
