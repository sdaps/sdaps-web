#!/usr/bin/env python3
from django.urls import path, re_path, include
from django.contrib.auth.decorators import permission_required

from sdaps_ctl.views import *

urlpatterns = [
    # generalprepost_matters: General views and Pre-/Postprocessing
    path('', SurveyList.as_view(), name='surveys'),
    path('create/', permission_required('sdaps_ctl.add_survey')
         (SurveyCreateView.as_view()), name='survey_create'),
    path('<slug:slug>/', include([
             path('', SurveyDetail.as_view(), name='survey_overview'),
             path('delete/', delete, name='survey_delete'),

             # designinit_matter: Designing the questionnaire and initializing
             path('edit/', SurveyUpdateView.as_view(),
                  name='questionnaire_edit'),
             path('edit/questionnaire/', questionnaire,
                  name='questionnaire_post'),
             path('questionnaire.pdf', questionnaire_download,
                  name='questionnaire_download'),
             path('questionnaire.tex', questionnaire_tex_download,
                  name='questionnaire_tex_download'),
             path('build/', survey_build, name='survey_build'),

             # upload_matter: Uploading scans for recognition
             path('add_scans/', SurveyAddScans.as_view(),
                  name='survey_add_scans'),
             path('upload/', SurveyUploadScansFiles.as_view(),
                  name='survey_upload_scans'),
             path('upload/<str:filename>/', SurveyUploadScansFiles.as_view(),
                  name='survey_upload_scans_file'),
             #re_path(r'^(?P<slug>\w+)/upload/(?P<filename>.+)$', SurveyUploadScansFiles.as_view(), name='survey_upload_scans'),

             # review_matter: Review the scans
             path('review/', survey_review, name='survey_review'),
             path('review/<int:sheet>/', survey_review_sheet,
                  name='survey_review_sheet'),
             path('scans/<int:filenum>/<int:page>/',
                  survey_scan, name='survey_scan'),

             # results_matters: Generate results and reports
             path('report/', survey_report, name='survey_report'),
             path('report.pdf', report_download, name='report_download'),
             path('data.csv', csv_download, name='csv_download'),
         ])),
]
