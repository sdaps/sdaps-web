
import os
import datetime

from .admin import SurveyAdmin

from django.conf.urls import patterns, include, url

from django.views import generic
from django.views.decorators import csrf
from django.views.decorators.http import last_modified

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.servers.basehttp import FileWrapper

from django.shortcuts import render, get_object_or_404

from django.template import Context, loader

import models
import tasks
import forms

def get_survey_or_404(request, survey_id, change=False):
    obj = get_object_or_404(models.Survey, id=survey_id)

    if change:
        if not request.user.has_perm('sdaps_ctl.change_survey'):
            raise Http404
    if not SurveyAdmin.has_permissions(request, obj):
        raise Http404

    return obj

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class SurveyList(LoginRequiredMixin, generic.ListView):
    template_name = 'list.html'
    context_object_name = 'survey_list'

    def get_queryset(self):
        return SurveyAdmin.filter(self.request, models.Survey.objects).order_by('name')

class SurveyDetail(LoginRequiredMixin, generic.DetailView):
    model = models.Survey
    template_name = 'overview.html'

    def get_object(self, *args, **kwargs):
        obj = generic.DetailView.get_object(self, *args, **kwargs)

        if obj and not SurveyAdmin.has_permissions(self.request, obj):
            raise Http404

        return obj

    def get_context_data(self, **kwargs):
        context = super(SurveyDetail, self).get_context_data(**kwargs)
        context['may_edit'] = self.request.user.has_perm('sdaps_ctl.change_survey')
        return context

# Questionnaire download last modified test
def questionnaire_last_modification(request, survey_id):
    survey = get_survey_or_404(request, survey_id)

    filename = os.path.join(survey.path, 'questionnaire.pdf')
    if not os.path.isfile(filename):
        raise Http404

    return datetime.datetime.utcfromtimestamp((os.stat(filename).st_ctime))


## Questionnaire download
@last_modified(questionnaire_last_modification)
@login_required
def questionaire_download(request, survey_id):
    survey = get_survey_or_404(request, survey_id)

    filename = os.path.join(survey.path, 'questionnaire.pdf')
    if not os.path.isfile(filename):
        raise Http404

    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/x-pdf')
    response['Content-Length'] = os.path.getsize(filename)
    response['Cache-Control'] = 'max-age=0, must-revalidate'

    return response

@login_required
def edit(request, survey_id):
    survey = get_survey_or_404(request, survey_id, change=True)

    # Get CSRF token, so that cookie will be included
    csrf.get_token(request)

    # XXX: Nicer error message?
    if survey.initialized:
        raise Http404

    context_dict = {
        'survey' : survey,
    }

    return render(request, 'edit_questionnaire.html', context_dict)

@login_required
def questionnaire(request, survey_id):
    survey = get_survey_or_404(request, survey_id, change=True)

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

