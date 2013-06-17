
import models

import os
import datetime

from django.conf.urls import patterns, include, url

from django.views.decorators.http import last_modified

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.servers.basehttp import FileWrapper

from django.shortcuts import render, get_object_or_404

from django.template import Context, loader

import tasks

def survey_list(request):
    survey_list = models.Survey.objects.order_by('name')

    template = loader.get_template('sdaps_ctl/list.html')

    context_dict = {
        'survey_list' : survey_list,
    }

    return render(request, 'sdaps_ctl/list.html', context_dict)

def survey_overview(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    return render(request, 'sdaps_ctl/overview.html', { 'survey' : survey })


# Questionnaire download last modified test
def questionnaire_last_modification(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    filename = os.path.join(survey.path, 'questionnaire.pdf')
    if not os.path.isfile(filename):
        raise Http404

    return datetime.datetime.utcfromtimestamp((os.stat(filename).st_ctime))


# Questionnaire download
@last_modified(questionnaire_last_modification)
def questionaire_download(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    filename = os.path.join(survey.path, 'questionnaire.pdf')
    if not os.path.isfile(filename):
        raise Http404

    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/x-pdf')
    response['Content-Length'] = os.path.getsize(filename)
    response['Cache-Control'] = 'must-revalidate'
    response['Expires'] = datetime.datetime.utcnow().ctime()

    return response


def edit_questionnaire(request, survey_id):
    survey = get_object_or_404(models.Survey, id=survey_id)

    # XXX: Nicer error message?
    if survey.initialized:
        raise Http404

    context_dict = {
        'survey' : survey,
    }

    #tex = open('/home/benjamin/Projects/sdaps/examples/example.tex').read()
    #tasks.update_questionnaire.delay(survey, tex)

    return render(request, 'sdaps_ctl/edit_questionnaire.html', context_dict)


urlpatterns = patterns('',
        url(r'^$', lambda x: HttpResponseRedirect('/list')),
        url(r'^list/?$', survey_list, name='list'),
        url(r'^survey/(?P<survey_id>\d+)/?$', survey_overview, name='survey_overview'),
        url(r'^survey/(?P<survey_id>\d+)/questionnaire.pdf$', questionaire_download, name='questionnaire_download'),
        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/?$', edit_questionnaire, name='questionnaire_edit'),
    )

