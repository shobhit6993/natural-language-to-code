import logging

from django.http import HttpResponse
from django.shortcuts import render, reverse

from ..core.configs import Configs as configs


def survey(request):
    return render(request, "turk/survey.html")


def save_survey(request):
    # Log survey data.
    user_id = request.session['user_id']
    file_path = configs.log_directory + str(user_id) + ".log"
    with open(file_path, 'a') as f:
        f.write("---survey---\n")
        f.write("easy:" + request.POST['easy'] + "\n")
        f.write("understand:" + request.POST['understand'] + "\n")
        f.write("sensible:" + request.POST['sensible'] + "\n")
        f.write("long:" + request.POST['long'] + "\n")
        comment = request.POST['comment'].replace('\r', ' ').replace('\n', ' ')
        f.write("comment:" + comment + "\n")
    logging.info("%s: Logged survey data.", user_id)

    return HttpResponse(reverse('turk:code'))
