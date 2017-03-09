from django.shortcuts import render


def sample_task(request):
    # Save true values of Channels and Functions in session.
    request.session['trigger_channel'] = 'Facebook'
    request.session['action_channel'] = 'Dropbox'
    request.session['trigger_fn'] = 'new_photo_post_by_you'
    request.session['action_fn'] = 'add_file_from_url'

    description = "When I add a photo on Facebook, save it to Dropbox."
    channels = ["Facebook", "Dropbox"]
    trigger_fns = ["new_status_message_by_you",
                   "new_status_message_by_you_with_hashtag",
                   "new_link_post_by_you",
                   "new_link_post_by_you_with_hashtag",
                   "new_photo_post_by_you",
                   "new_photo_post_by_you_with_hashtag",
                   "new_photo_post_by_you_in_area"]
    action_fns = ["add_file_from_url", "create_a_text_file",
                  "append_to_a_text_file"]
    context = {'channels': channels, 'trigger_fns': trigger_fns,
               'action_fns': action_fns, 'description': description}
    return render(request, 'turk/sample_task.html', context)


def sample_conversation(request):
    description = "When I add a photo on Facebook, save it to Dropbox."
    trigger_channel = "Facebook"
    action_channel = "Dropbox"
    trigger_fn = "new_photo_post_by_you"
    action_fn = "add_file_from_url"
    context = {'trigger_channel': trigger_channel, 'trigger_fn': trigger_fn,
               'action_channel': action_channel, 'action_fn': action_fn,
               'description': description}
    return render(request, 'turk/sample_conversation.html', context)
