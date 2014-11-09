
import os
import datetime

from django.conf.urls import patterns, include, url

from django.views import generic
from django.views.decorators import csrf
from django.views.decorators.http import last_modified

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.servers.basehttp import FileWrapper

from django.shortcuts import render, get_object_or_404

from django.template import Context, loader

import models
import tasks
import forms

class SurveyList(generic.ListView):
    template_name = 'sdaps_ctl/list.html'
    context_object_name = 'survey_list'

    def get_queryset(self):
        return models.Survey.objects.order_by('name')

class SurveyDetail(generic.DetailView):
    model = models.Survey
    template_name = 'sdaps_ctl/overview.html'

# Questionnaire download last modified test
def questionnaire_last_modification(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    filename = os.path.join(survey.path, 'questionnaire.pdf')
    if not os.path.isfile(filename):
        raise Http404

    return datetime.datetime.utcfromtimestamp((os.stat(filename).st_ctime))


## Questionnaire download
@last_modified(questionnaire_last_modification)
def questionaire_download(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    filename = os.path.join(survey.path, 'questionnaire.pdf')
    if not os.path.isfile(filename):
        raise Http404

    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/x-pdf')
    response['Content-Length'] = os.path.getsize(filename)
    response['Cache-Control'] = 'max-age=0, must-revalidate'

    return response

def edit(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    # Get CSRF token, so that cookie will be included
    csrf.get_token(request)

    # XXX: Nicer error message?
    if survey.initialized:
        raise Http404

    context_dict = {
        'survey' : survey,
    }

    return render(request, 'sdaps_ctl/edit_questionnaire.html', context_dict)

def questionnaire(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    # Get CSRF token, so that cookie will be included
    csrf.get_token(request)

    # XXX: Nicer error message?
    if survey.initialized:
        raise Http404

    if request.method == 'POST':
        survey.questionnaire = request.read()
        survey.save()
        tasks.queue_timed_write_and_render(survey)

    return HttpResponse(survey.questionnaire)


urlpatterns = patterns('',
        url(r'^$', lambda x: HttpResponseRedirect('/surveys')),
        url(r'^surveys/?$', SurveyList.as_view(), name='surveys'),
        url(r'^surveys/(?P<pk>\d+)/?$', SurveyDetail.as_view(), name='survey_overview'),
        url(r'^surveys/(?P<survey_id>\d+)/questionnaire.pdf$', questionaire_download, name='questionnaire_download'),
        url(r'^surveys/(?P<survey_id>\d+)/edit/?$', edit, name='questionnaire_edit'),
        url(r'^surveys/(?P<survey_id>\d+)/edit/questionnaire?$', questionnaire, name='questionnaire_post'),
#        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/qobjects/(?P<pk>\d+)/$', QuestionDetail.as_view()),
#        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/answers/$', AnswerList.as_view()),
#        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/answers/(?P<pk>\d+)/$', AnswerDetail.as_view()),
    )

