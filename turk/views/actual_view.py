import logging

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from ..core.configs import Configs as configs
from ..core.dialog_agent import create_dialog_agent, get_intent
from ..core.recipes import Recipes
from ..core.parsers import Parsers

def actual_task(request):
    def log_task(recipe):
        user_id = request.session['user_id']
        file_path = configs.log_directory + str(user_id) + ".log"
        with open(file_path, 'a') as f:
            f.write("session_id:" + str(request.session.session_key) + "\n")
            f.write("recipe_url:" + recipe['url'] + "\n")
            f.write("short_description:" + recipe['name'] + "\n")
            f.write("long_description:" + recipe['description'] + "\n")
            f.write("trigger_channel:" + recipe['trigger_channel'] + "\n")
            f.write("trigger_function:" + recipe['trigger_function'] + "\n")
            f.write("action_channel:" + recipe['action_channel'] + "\n")
            f.write("action_function:" + recipe['action_function'] + "\n")
        logging.info("%s: Logged task information.", user_id)

    # recipe = Recipes.randomly_pick_recipe()
    recipe = Recipes.next_recipe()
    logging.debug("Chosen recipe: %s", recipe)

    # Save true values of Channels, Functions, and other recipe details
    # in the session.
    request.session['trigger_channel'] = recipe['trigger_channel']
    request.session['action_channel'] = recipe['action_channel']
    request.session['trigger_fn'] = recipe['trigger_function']
    request.session['action_fn'] = recipe['action_function']
    request.session['recipe_url'] = recipe['url']
    request.session['recipe_index'] = recipe['index']
    request.session['short_description'] = recipe['name']
    request.session['long_description'] = recipe['description']

    # Log recipe details
    log_task(recipe)

    context = {'trigger_channel': recipe['trigger_channel'],
               'trigger_fn': recipe['trigger_function'],
               'action_fn': recipe['action_function'],
               'action_channel': recipe['action_channel'],
               'short_description': recipe['name'],
               'long_description': recipe['description']}
    return render(request, 'turk/actual_task.html', context)


def actual_conversation(request):
    # Create a new dialog agent for the conversation, and save it in session.
    dialog_agent = create_dialog_agent()
    request.session['dialog_agent'] = dialog_agent

    short_description = request.session['short_description']
    long_description = request.session['long_description']
    trigger_channel = request.session['trigger_channel']
    action_channel = request.session['action_channel']
    trigger_fn = request.session['trigger_fn']
    action_fn = request.session['action_fn']
    context = {'trigger_channel': trigger_channel, 'trigger_fn': trigger_fn,
               'action_channel': action_channel, 'action_fn': action_fn,
               'short_description': short_description,
               'long_description': long_description}
    return render(request, 'turk/actual_conversation.html', context)


def first_utterance(request):
    def log_utterance(sys_utterance):
        user_id = request.session['user_id']
        file_path = configs.log_directory + str(user_id) + ".log"
        with open(file_path, 'a') as f:
            f.write("---conversation---\n")
            f.write("ROBOT:" + sys_utterance + "\n")
        logging.info("%s: Logged first system utterance.", user_id)

    sys_utterance = request.session['dialog_agent'].open_dialog()
    request.session.modified = True
    # Log system utterance
    log_utterance(sys_utterance)
    return HttpResponse(sys_utterance)


def read_user_utterance(request):
    def log_utterances(user_utterance, sys_utterance):
        user_id = request.session['user_id']
        file_path = configs.log_directory + str(user_id) + ".log"
        with open(file_path, 'a') as f:
            f.write("USER:" + user_utterance + "\n")
            f.write("ROBOT:" + sys_utterance + "\n")
        logging.info("%s: Logged user and system utterances.", user_id)

    try:
        user_utterance = request.POST['user_utterance'].lower().strip()
        dialog_agent = request.session['dialog_agent']
        sys_utterance = dialog_agent.generate_system_response(
            user_utterance, Parsers.utterance_parser)
        intention = get_intent(sys_utterance)

        # Log user and system utterances
        log_utterances(user_utterance, sys_utterance)
        request.session.modified = True

        # If this is the end of conversation, mark the recipe as used.
        if intention == "close":
            Recipes.mark_recipe_as_used(request.session['recipe_index'])

        return JsonResponse({"system_utterance": sys_utterance,
                             "intent": intention})
    except Exception:
        logging.error("`user_utterance` not in POST request %s", request)
        raise
