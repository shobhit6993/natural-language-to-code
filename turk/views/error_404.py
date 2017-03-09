from django.http import Http404


def error_404(request):
    raise Http404
