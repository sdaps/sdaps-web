
import os
import datetime

from django.conf.urls import patterns, include, url

from django.views.decorators.http import last_modified

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.servers.basehttp import FileWrapper

from django.shortcuts import render, get_object_or_404

from django.template import Context, loader

from rest_framework import response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status

import models
import serializers
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

    tex = open('/home/benjamin/Projects/sdaps/examples/example.tex').read()
    tasks.update_questionnaire.delay(survey, tex)

    return render(request, 'sdaps_ctl/edit_questionnaire.html', context_dict)


######################################
# And the REST API
######################################
class QuestionList(mixins.ListModelMixin,
                   generics.GenericAPIView):

    # XXX: No idea why this helps, but we don't have permissions right now
    #      anyways.
    _ignore_model_permissions = True

    def get_queryset(self):
        surveyid = self.kwargs['survey_id']

        return models.QObject.objects.filter(survey=models.Survey.objects.get(id=surveyid))

    serializer_class = serializers.QObjectSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # We need to set the survey ID.

        survey = get_object_or_404(models.Survey, id=kwargs['survey_id'])

        serializer = self.serializer_class(data=request.DATA, context={'survey': survey})

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return self.create(request, *args, **kwargs)

class QuestionDetail(generics.GenericAPIView):
    # XXX: No idea why this helps, but we don't have permissions right now
    #      anyways.
    _ignore_model_permissions = True

    def get_object(self, pk, survey_id):
        try:
             qobject = models.QObject.objects.get(pk=pk)

             if qobject.survey_id != int(self.kwargs['survey_id']):
                raise models.QObject.DoesNotExist

             return qobject
        except models.QObject.DoesNotExist:
            raise Http404

    serializer_class = serializers.QObjectSerializer

    def get(self, request, pk, survey_id, format=None):
        qobject = self.get_object(pk, survey_id)
        serializer = self.serializer_class(qobject)
        return response.Response(serializer.data)

    def put(self, request, pk, survey_id, format=None):
        qobject = self.get_object(pk, survey_id)
        serializer = self.serializer_class(qobject, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, survey_id, format=None):
        qobject = self.get_object(pk, survey_id)
        qobject.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


# Answers
class AnswerList(mixins.ListModelMixin,
                 generics.GenericAPIView):

    # XXX: No idea why this helps, but we don't have permissions right now
    #      anyways.
    _ignore_model_permissions = True

    def get_queryset(self):
        return models.QAnswer.objects.filter(qobject__survey_id__exact=self.kwargs['survey_id'])

    serializer_class = serializers.QAnswerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # We need to set the survey ID.

        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return self.create(request, *args, **kwargs)

class AnswerDetail(generics.GenericAPIView):
    # XXX: No idea why this helps, but we don't have permissions right now
    #      anyways.
    _ignore_model_permissions = True

    def get_object(self, pk, survey_id):
        try:
             qanswer = models.QAnswer.objects.get(pk=pk)
             if qanswer.qobject.survey_id != int(survey_id):
                 raise models.QAnswer.DoesNotExist

             return qanswer
        except models.QAnswer.DoesNotExist:
            raise Http404

    serializer_class = serializers.QAnswerSerializer

    def get(self, request, pk, survey_id, format=None):
        qanswer = self.get_object(pk, survey_id)
        serializer = self.serializer_class(qanswer)

        return response.Response(serializer.data)

    def put(self, request, pk, survey_id, format=None):
        qanswer = self.get_object(pk, survey_id)
        serializer = self.serializer_class(qanswer, data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, survey_id, format=None):
        qanswer = self.get_object(pk, survey_id)
        qanswer.delete()

        return response.Response(status=status.HTTP_204_NO_CONTENT)



urlpatterns = patterns('',
        url(r'^$', lambda x: HttpResponseRedirect('/list')),
        url(r'^list/?$', survey_list, name='list'),
        url(r'^survey/(?P<survey_id>\d+)/?$', survey_overview, name='survey_overview'),
        url(r'^survey/(?P<survey_id>\d+)/questionnaire.pdf$', questionaire_download, name='questionnaire_download'),
        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/?$', edit_questionnaire, name='questionnaire_edit'),
        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/qobjects/$', QuestionList.as_view()),
        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/qobjects/(?P<pk>\d+)/$', QuestionDetail.as_view()),
        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/answers/$', AnswerList.as_view()),
        url(r'^survey/(?P<survey_id>\d+)/edit/questionnaire/answers/(?P<pk>\d+)/$', AnswerDetail.as_view()),
    )

