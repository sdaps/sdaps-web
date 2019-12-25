from django.urls import path, re_path
from django.contrib.auth.decorators import permission_required

from sdaps_ctl.views import *

urlpatterns = [
        # generalprepost_matters: General views and Pre-/Postprocessing
        path('', SurveyList.as_view(), name='surveys'),
        path('create/', permission_required('sdaps_ctl.add_survey')(SurveyCreateView.as_view()), name='survey_create'),
        path('<slug:slug>/', SurveyDetail.as_view(), name='survey_overview'),
        path('<slug:slug>/delete/', delete, name='survey_delete'),

        # designinit_matter: Designing the questionnaire and initializing
        path('<slug:slug>/edit/', SurveyUpdateView.as_view(), name='questionnaire_edit'),
        path('<slug:slug>/edit/questionnaire/', questionnaire, name='questionnaire_post'),
        path('<slug:slug>/questionnaire.pdf', questionnaire_download, name='questionnaire_download'),
        path('<slug:slug>/questionnaire.tex', questionnaire_tex_download, name='questionnaire_tex_download'),
        path('<slug:slug>/build/', survey_build, name='survey_build'),

        # upload_matter: Uploading scans for review
        path('<slug:slug>/add_scans/', survey_add_scans, name='survey_add_scans'),
        path('<slug:slug>/upload/', survey_upload_scans, name='survey_upload_scans'),
        path('<slug:slug>/upload/post/', SurveyUploadScansPost.as_view(), name='survey_upload_scans_post'),
        re_path(r'^(?P<slug>\w+)/upload/post/(?P<filename>.+)$', SurveyUploadScansFile.as_view(), name='survey_upload_scans_file'),

        # review_matter: Review the scans
        path('<slug:slug>/review/', survey_review, name='survey_review'),
        path('<slug:slug>/review/<int:sheet>/', survey_review_sheet, name='survey_review_sheet'),
        path('<slug:slug>/scans/<int:filenum>/<int:page>/', survey_scan, name='survey_scan'),

        # results_matters: Generate results and reports
        path('<slug:slug>/report/', survey_report, name='survey_report'),
        path('<slug:slug>/report.pdf', report_download, name='report_download'),
        path('<slug:slug>/data.csv', csv_download, name='csv_download'),
    ]
