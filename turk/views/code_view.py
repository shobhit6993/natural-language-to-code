from django.shortcuts import render


def code(request):
    context = {"code": request.session['user_id']}
    return render(request, "turk/code.html", context)
