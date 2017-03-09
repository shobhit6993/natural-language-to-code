import logging
import os
from random import randrange

from django.shortcuts import render
from ..core.configs import Configs as configs

def index(request):
    user_id = randrange(1000000000, 9999999999)
    request.session['user_id'] = user_id

    # Create log-file
    while True:
        file_path = configs.log_directory + str(user_id) + ".log"
        if os.path.isfile(file_path):
            continue
        with open(file_path, 'a') as f:
            f.write("user_id:" + str(user_id) + "\n")
        logging.info("%s: Created log file, and logged user ID.", user_id)
        break

    return render(request, 'turk/index.html')
