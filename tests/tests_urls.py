from django.test import SimpleTestCase
from django.urls import reverse, resolve
from sdaps_ctl.views import *

class TestUrls(SimpleTestCase):
    def test_surveylist_url_resolves(self):
        url = reverse('surveys')
        self.assertEquals(resolve(url).func.view_class, SurveyList)

    def test_surveycreate_url_resolves(self):
        url = reverse('survey_create')
        self.assertEquals(resolve(url).func.view_class, SurveyCreateView)

    def test_surveyoverview_url_resolves(self):
        url = reverse('survey_overview', args=['some-slug'])
        self.assertEquals(resolve(url).func.view_class, SurveyDetail)

    def test_surveycsvdownload_url_resolves(self):
        url = reverse('csv_download', args=['some-slug'])
        self.assertEquals(resolve(url).func, csv_download)

    def test_surveyquestionnairedownload_url_resolves(self):
        url = reverse('questionnaire_download', args=['some-slug'])
        self.assertEquals(resolve(url).func, questionnaire_download)

    def test_surveyquestionnairetexdownload_url_resolves(self):
        url = reverse('questionnaire_tex_download', args=['some-slug'])
        self.assertEquals(resolve(url).func, questionnaire_tex_download)

    def test_surveyreportdownload_url_resolves(self):
        url = reverse('report_download', args=['some-slug'])
        self.assertEquals(resolve(url).func, report_download)

    def test_surveyquestionnaireedit_url_resolves(self):
        url = reverse('questionnaire_edit', args=['some-slug'])
        self.assertEquals(resolve(url).func.view_class, SurveyUpdateView)

    def test_surveydelete_url_resolves(self):
        url = reverse('survey_delete', args=['some-slug'])
        self.assertEquals(resolve(url).func, delete)

    def test_surveyquestionnairepost_url_resolves(self):
        url = reverse('questionnaire_post', args=['some-slug'])
        self.assertEquals(resolve(url).func, questionnaire)

    def test_surveyreview_url_resolves(self):
        url = reverse('survey_review', args=['some-slug'])
        self.assertEquals(resolve(url).func, survey_review)

    def test_surveyreviewsheet_url_resolves(self):
        url = reverse('survey_review_sheet', kwargs={'slug':'some-slug', 'sheet': 1})
        self.assertEquals(resolve(url).func, survey_review_sheet)

    def test_surveyscan_url_resolves(self):
        url = reverse('survey_scan', kwargs={'slug':'some-slug', 'filenum': 1, 'page': 1})
        self.assertEquals(resolve(url).func, survey_scan)

    def test_surveybuild_url_resolves(self):
        url = reverse('survey_build', args=['some-slug'])
        self.assertEquals(resolve(url).func, survey_build)

    def test_surveyreport_url_resolves(self):
        url = reverse('survey_report', args=['some-slug'])
        self.assertEquals(resolve(url).func, survey_report)

    def test_surveyaddscans_url_resolves(self):
        url = reverse('survey_add_scans', args=['some-slug'])
        self.assertEquals(resolve(url).func, survey_add_scans)

    def test_surveyuploadscans_url_resolves(self):
        url = reverse('survey_upload_scans', args=['some-slug'])
        self.assertEquals(resolve(url).func, survey_upload_scans)

    def test_surveyuploadscanspost_url_resolves(self):
        url = reverse('survey_upload_scans_post', args=['some-slug'])
        self.assertEquals(resolve(url).func.view_class, SurveyUploadScansPost)

    def test_surveyuploadscansfile_url_resolves(self):
        url = reverse('survey_upload_scans_file', args={'slug':'some-slug', 'filename': 1})
        self.assertEquals(resolve(url).func.view_class, SurveyUploadScansFile)

    def test_redirecttosurveyscanslist_url_resolves(self):
        url = reverse('survey_upload_scans_file', args={'slug':'some-slug', 'filename': 1})
        self.assertEquals(resolve(url).func.view_class, SurveyUploadScansFile) 
