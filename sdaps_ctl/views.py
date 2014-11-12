
import os
import os.path
import datetime

from .admin import SurveyAdmin

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse

from django.views import generic
from django.views.decorators import csrf
from django.views.decorators.http import last_modified

from django.contrib.auth.decorators import login_required, permission_required

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.servers.basehttp import FileWrapper

from django.shortcuts import render, get_object_or_404

from django.template import Context, loader

import models
import tasks
import forms

import simplejson as json

from sdaps.model.survey import Survey as SDAPSSurvey
from sdaps import image
from sdaps import matrix
from . import buddies
import cairo

def get_survey_or_404(request, survey_id, change=False, delete=False, review=False):
    obj = get_object_or_404(models.Survey, id=survey_id)

    if change:
        if not request.user.has_perm('sdaps_ctl.change_survey'):
            raise Http404
    if delete:
        if not request.user.has_perm('sdaps_ctl.delete_survey'):
            raise Http404
    if delete:
        if not request.user.has_perm('sdaps_ctl.review_survey'):
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

@permission_required('sdaps_ctl.add_survey')
def survey_create(request):
    if request.method == "POST":
        # We want to update the survey from the form
        form = forms.SurveyForm(request.POST)

        if form.is_valid():
            survey = form.save(commit=False)
            survey.owner = request.user
            survey.save()

            # Rendering the empty document does not really hurt ...
            tasks.queue_timed_write_and_render(survey)

            return HttpResponseRedirect(reverse('questionnaire_edit', args=(survey.id,)))
    else:
        form = forms.SurveyForm()

    context_dict = {
        'main_form' : form,
    }

    return render(request, 'survey_create.html', context_dict)


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
        context['may_delete'] = self.request.user.has_perm('sdaps_ctl.delete_survey')
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

    if request.method == "POST":
        # We want to update the survey from the form
        form = forms.SurveyForm(request.POST, instance=survey)

        if form.is_valid():
            form.save()
            tasks.queue_timed_write_and_render(survey)
    else:
        form = forms.SurveyForm(instance=survey)

    context_dict = {
        'main_form' : form,
        'survey' : survey,
    }

    return render(request, 'edit_questionnaire.html', context_dict)

@login_required
def delete(request, survey_id):
    survey = get_survey_or_404(request, survey_id, delete=True)

    yes_missing = False
    if request.method == "POST":
        if 'delete' in request.POST and request.POST['delete'] == "YES":
            survey.delete()
            return HttpResponseRedirect(reverse('surveys'))
        else:
            yes_missing = True

    return render(request, 'delete.html', { 'survey' : survey, 'yes_missing' : yes_missing })

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

@login_required
def survey_image(request, survey_id, filenum, page):
    # This function does not open the real SDAPS survey, as unpickling the data
    # is way to inefficient.
    survey = get_survey_or_404(request, survey_id, review=True)

    image_file = os.path.join(survey.path, "%s.tif" % (filenum,))

    if not os.path.exists(os.path.join(survey.path)):
        raise Http404

    surface = image.get_rgb24_from_tiff(image_file, int(page), False)
    if surface is None:
        raise Http404

    # Create PNG stream and return it
    response = HttpResponse(content_type='image/png')
    response['Cache-Control'] = 'private, max-age=3600'
    surface.write_to_png(response)

    return response

@login_required
def survey_review(request, survey_id):
    djsurvey = get_survey_or_404(request, survey_id, review=True)

    if not djsurvey.initialized:
        raise Http404

    context_dict = {
        'survey' : djsurvey
    }

    return render(request, 'survey_review.html', context_dict)

@login_required
def survey_review_sheet(request, survey_id, sheet):
    djsurvey = get_survey_or_404(request, survey_id, review=True)

    # Get CSRF token, so that cookie will be included
    csrf.get_token(request)

    sheet = int(sheet)

    # TODO: Nicer error message?
    if not djsurvey.initialized:
        raise Http404

    # Now this is getting hairy, we need to unpickle the data :-(
    with models.LockedSurvey(djsurvey.id):

        survey = SDAPSSurvey.load(djsurvey.path)

        try:
            survey.index = sheet
        except KeyError:
            raise Http404

        if request.method == 'POST':
            post_data = json.loads(res)
            data = post_data['data']

            survey.questionnaire.sdaps_ctl.set_data(data)

        # Assume image is NUMBER.tif
        res = {
            'images' : [
                {
                    'image' : int(image.filename[:-4]),
                    'page' : image.page_number,
                    'rotated' : image.rotated,
                    'pxtomm' : tuple(image.matrix.px_to_mm()),
                    'mmtopx' : tuple(image.matrix.mm_to_px()),
                } for image in survey.sheet.images if not image.ignored
            ],
            'data' : survey.questionnaire.sdaps_ctl.get_data()
        }

        return HttpResponse(json.dumps(res))

urlpatterns = patterns('',
        url(r'^$', lambda x: HttpResponseRedirect('/surveys')),
        url(r'^surveys/?$', SurveyList.as_view(), name='surveys'),
        url(r'^surveys/create/?$', survey_create, name='survey_create'),
        url(r'^surveys/(?P<pk>\d+)/?$', SurveyDetail.as_view(), name='survey_overview'),
        url(r'^surveys/(?P<survey_id>\d+)/questionnaire.pdf$', questionaire_download, name='questionnaire_download'),
        url(r'^surveys/(?P<survey_id>\d+)/edit/?$', edit, name='questionnaire_edit'),
        url(r'^surveys/(?P<survey_id>\d+)/delete/?$', delete, name='survey_delete'),
        url(r'^surveys/(?P<survey_id>\d+)/edit/questionnaire/?$', questionnaire, name='questionnaire_post'),

        url(r'^surveys/(?P<survey_id>\d+)/review/?$', survey_review, name='survey_review'),
        url(r'^surveys/(?P<survey_id>\d+)/review/(?P<sheet>\d+)/?$', survey_review_sheet, name='survey_review_sheet'),
        url(r'^surveys/(?P<survey_id>\d+)/images/(?P<filenum>\d+)/(?P<page>\d+)/?$', survey_image, name='survey_image'),
    )

