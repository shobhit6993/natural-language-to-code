from __future__ import absolute_import

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^sample_task/*$',
        views.sample_task, name="sample_task"),
    url(r'^check_answers/*$', views.check_answers,
        name="check_answers"),
    url(r'^sample_conversation/*$', views.sample_conversation,
        name="sample_conversation"),
    url(r'^actual_task/*$', views.actual_task, name="actual_task"),
    url(r'^actual_conversation/*$', views.actual_conversation,
        name="actual_conversation"),
    url(r'^first_utterance/*$', views.first_utterance, name="first_utterance"),
    url(r'^read_user_utterance/*$', views.read_user_utterance,
        name="read_user_utterance"),
    url(r'^survey/*$', views.survey, name="survey"),
    url(r'^save_survey/*$', views.save_survey, name="save_survey"),
    url(r'^code/*', views.code, name="code"),
    url(r'.*', views.error_404, name="error_404")
]
