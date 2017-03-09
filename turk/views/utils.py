from django.http import HttpResponse

def check_answers(request):
    ans = request.POST

    if (ans['trigger_channel'] == request.session['trigger_channel'] and
                ans['action_channel'] == request.session['action_channel'] and
                ans['trigger_fn'] == request.session['trigger_fn'] and
                ans['action_fn'] == request.session['action_fn']):
        return HttpResponse("correct")
    else:
        return HttpResponse("incorrect")
