
import os
import os.path
import datetime

import re

from .admin import SurveyAdmin

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse

from django.views import generic
from django.views.decorators import csrf
from django.views.decorators.http import last_modified

from django.contrib.auth.decorators import login_required, permission_required

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.files.base import ContentFile
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

def get_survey_or_404(request, survey_id, change=False, delete=False, review=False, upload=False):
    obj = get_object_or_404(models.Survey, id=survey_id)

    if change:
        if not request.user.has_perm('sdaps_ctl.change_survey'):
            raise Http404
    if delete:
        if not request.user.has_perm('sdaps_ctl.delete_survey'):
            raise Http404
    if review:
        if not request.user.has_perm('sdaps_ctl.review_survey'):
            raise Http404
    if upload:
        if not request.user.has_perm('sdaps_ctl.change_uploadedfile'):
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

@login_required
def survey_add_images(request, survey_id):
    if request.method == "POST":
        survey = get_survey_or_404(request, survey_id, change=True)

        if survey.active_task:
            raise Http404

        # Queue file addition
        tasks.queue_add_and_recognize(survey)

        return HttpResponseRedirect(reverse('survey_overview', args=(survey.id,)))

    # XXX: Everything else is not allowed
    raise Http404

@login_required
def survey_build(request, survey_id):
    if request.method == "POST":
        survey = get_survey_or_404(request, survey_id, change=True)

        if survey.initialized:
            raise Http404

        if survey.active_task:
            raise Http404

        # Queue project creation
        tasks.queue_build_survey(survey)

        return HttpResponseRedirect(reverse('survey_overview', args=(survey.id,)))

    # XXX: Everything else is not allowed
    raise Http404

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
        context['may_upload'] = self.request.user.has_perm('sdaps_ctl.change_uploadedfile')
        context['may_review'] = self.request.user.has_perm('sdaps_ctl.review_survey')
        context['may_change'] = self.request.user.has_perm('sdaps_ctl.change_survey')
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
def questionnaire_download(request, survey_id):
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

    return HttpResponse(survey.questionnaire, content_type="application/json")

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

    # XXX: Throw sane error in this case!
    if djsurvey.active_task:
        raise Http404

    with models.LockedSurvey(djsurvey.id, 5):

        survey = SDAPSSurvey.load(djsurvey.path)

        context_dict = {
            'survey' : djsurvey,
            'sheet_count' : len(survey.sheets)
        }

        return render(request, 'survey_review.html', context_dict)

@login_required
def survey_review_sheet(request, survey_id, sheet):
    djsurvey = get_survey_or_404(request, survey_id, review=True)

    # Get CSRF token, so that cookie will be included
    csrf.get_token(request)

    sheet = int(sheet)

    # XXX: Throw sane error in this case!
    if djsurvey.active_task:
        raise Http404

    if not djsurvey.initialized:
        raise Http404

    # Now this is getting hairy, we need to unpickle the data :-(
    with models.LockedSurvey(djsurvey.id, 5):

        survey = SDAPSSurvey.load(djsurvey.path)

        try:
            survey.index = sheet
        except KeyError:
            raise Http404

        if request.method == 'POST':
            post_data = json.loads(request.read())
            data = post_data['data']

            survey.questionnaire.sdaps_ctl.set_data(data)

            survey.save()

        # Assume image is NUMBER.tif
        res = {
            'images' : [
                {
                    'image' : int(image.filename[:-4]),
                    'image_page' : image.tiff_page,
                    'page' : image.page_number if image.survey_id == survey.survey_id else -1,
                    'rotated' : image.rotated,
                    'pxtomm' : tuple(image.matrix.px_to_mm()),
                    'mmtopx' : tuple(image.matrix.mm_to_px()),
                } for image in survey.sheet.images if not image.ignored
            ],
            'data' : survey.questionnaire.sdaps_ctl.get_data()
        }

        return HttpResponse(json.dumps(res), content_type="application/json")



@login_required
def survey_upload(request, survey_id):
    survey = get_survey_or_404(request, survey_id, upload=True)

    # XXX: Throw sane error in this case!
    if survey.active_task:
        raise Http404

    csrf.get_token(request)

    if not survey.initialized:
        raise Http404

    context_dict = {
        'survey' : survey,
    }

    return render(request, 'survey_upload.html', context_dict)



class SurveyUploadPost(LoginRequiredMixin, generic.View):

    content_range_pattern = re.compile(r'^bytes (?P<start>\d+)-(?P<end>\d+)/(?P<size>\d+)')

    def ensure_valid_upload(self, upload):
        if upload.status != models.UPLOADING:
            return False
        return True

    def post(self, request, survey_id):
        survey = get_survey_or_404(self.request, survey_id, upload=True)

        # XXX: Throw sane error in this case!
        if survey.active_task:
            raise Http404

        #upload_id = request.POST.get('upload_id')

        single_file = len(request.FILES.getlist('files[]')) == 1
        result = list()
        range_header = None
        for chunk in request.FILES.getlist('files[]'):
            # Get the details about the chunk/upload
            content_range = request.META.get('HTTP_CONTENT_RANGE', '')
            if content_range:
                match = self.content_range_pattern.match(content_range)
                if not match:
                    result.append({ 'name' : chunk.name, 'error' : 'Broken or wrong content range.' })
                    continue

                start = int(match.group('start'))
                end = int(match.group('end'))
                length = int(match.group('size'))

                size = end - start + 1
            else:
                start = 0
                size = None

                length = chunk.size

            # TODO: Figure out a way that name collisions work!
            upload = models.UploadedFile.objects.filter(survey=survey, filename=chunk.name).first()

            if upload is not None:
                if not self.ensure_valid_upload(upload):
                    result.append({ 'name' : chunk.name, 'error' : 'File already uploaded or in an error state.' })
                    continue

            else:
                # Create a new upload
                upload = models.UploadedFile(survey=survey, filename=chunk.name, filesize=length)
                # Ensure PK is created
                upload.save()
                upload.file.save(name='', content=ContentFile(''), save=True)

            upload.append_chunk(chunk, offset=start, length=size)

            upload.save()

            result.append(upload.get_description())

            if single_file:
                # Send back the range that is already uploaded
                range_header = 'bytes %i-%i' % (0, upload.file.size-1)

        # only include the uploaded files in response
        result = {
            'files' : result,
        }

        response = HttpResponse(json.dumps(result), content_type="application/json")
        if range_header is not None:
            response['Range'] = range_header

        return response

    def generate_response(self, survey):
        files = list(survey.uploads.all())
        result = []
        for f in files:
            result.append(f.get_description())

        result = {
            'files' : result,
        }

        return HttpResponse(json.dumps(result), content_type="application/json")


    def get(self, request, survey_id):
        survey = get_survey_or_404(self.request, survey_id, upload=True)

        return self.generate_response(survey)


class SurveyUploadFile(LoginRequiredMixin, generic.View):

    def delete(self, request, survey_id, filename):
        survey = get_survey_or_404(self.request, survey_id, upload=True)

        # XXX: Throw sane error in this case!
        if survey.active_task:
            raise Http404

        upload = models.UploadedFile.objects.filter(survey=survey, filename=filename).first()
        upload.delete()

        return HttpResponse(json.dumps({ 'files' : [ { filename : True }] }), content_type="application/json")


    def get(self, request, survey_id, filename):
        survey = get_survey_or_404(self.request, survey_id, upload=True)

        upload = models.UploadedFile.objects.filter(survey=survey, filename=filename).first()

        if upload is None:
            raise Http404

        # XXX: Store mimetype and return correct one here!
        return HttpResponse(upload.file, content_type="application/binary")

urlpatterns = patterns('',
        url(r'^$', lambda x: HttpResponseRedirect('/surveys')),
        url(r'^surveys/?$', SurveyList.as_view(), name='surveys'),
        url(r'^surveys/create/?$', survey_create, name='survey_create'),
        url(r'^surveys/(?P<pk>\d+)/?$', SurveyDetail.as_view(), name='survey_overview'),
        url(r'^surveys/(?P<survey_id>\d+)/questionnaire.pdf$', questionnaire_download, name='questionnaire_download'),
        url(r'^surveys/(?P<survey_id>\d+)/edit/?$', edit, name='questionnaire_edit'),
        url(r'^surveys/(?P<survey_id>\d+)/delete/?$', delete, name='survey_delete'),
        url(r'^surveys/(?P<survey_id>\d+)/edit/questionnaire/?$', questionnaire, name='questionnaire_post'),

        url(r'^surveys/(?P<survey_id>\d+)/review/?$', survey_review, name='survey_review'),
        url(r'^surveys/(?P<survey_id>\d+)/review/(?P<sheet>\d+)/?$', survey_review_sheet, name='survey_review_sheet'),
        url(r'^surveys/(?P<survey_id>\d+)/images/(?P<filenum>\d+)/(?P<page>\d+)/?$', survey_image, name='survey_image'),

        url(r'^surveys/(?P<survey_id>\d+)/build/?$', survey_build, name='survey_build'),
        url(r'^surveys/(?P<survey_id>\d+)/add_images/?$', survey_add_images, name='survey_add_images'),
        url(r'^surveys/(?P<survey_id>\d+)/upload/?$', survey_upload, name='survey_upload'),
        url(r'^surveys/(?P<survey_id>\d+)/upload/post/?$', SurveyUploadPost.as_view(), name='survey_upload_post'),
        url(r'^surveys/(?P<survey_id>\d+)/upload/post/(?P<filename>.+)$', SurveyUploadFile.as_view(), name='survey_upload_file'),
    )

