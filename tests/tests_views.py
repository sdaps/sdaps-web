import shutil
import json
import os

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

from sdaps_ctl.models import Survey
import sdaps_ctl.urls

class TestPreSurveyInitViews(TestCase):

    def setUp(self):
        if not os.path.isdir(settings.SDAPS_PROJECT_ROOT):
            print('Project root does not exists. Create directory.')
            os.mkdir(settings.SDAPS_PROJECT_ROOT)
        else:
            if os.path.isdir(settings.SDAPS_PROJECT_ROOT+"/deleted"):
                shutil.rmtree(settings.SDAPS_PROJECT_ROOT + '/deleted', ignore_errors=True)
        self.client = Client()
        self.testslug = '123ABC'

        # Oriented via matters of "urls.py"
        # generalprepost_matters
        self.surveylist_url = reverse('surveys')
        self.surveycreate_url = reverse('survey_create')
        self.surveyoverview_url = reverse('survey_overview', args=[self.testslug])
        self.surveydelete_url = reverse('survey_delete', args=[self.testslug])
        # designinit_matter
        #self.questionnaireedit_url = reverse('questionnaire_edit', args=[self.testslug])
        self.surveyquestionnairepost_url = reverse('questionnaire_post', args=[self.testslug])
        #self.questionnairedownload_url = reverse('questionnaire_download', args=[self.testslug])
        #self.questionnairetexdownload_url = reverse('questionnaire_tex_download', args=[self.testslug])
        #self.surveybuild_url = reverse('survey_build', args=[self.testslug])

        self.json_questionnaire = json.dumps('[{"text":"Text","type":"textbody"},{"title":"Title","type":"section"},{"columns":2,"type":"multicol","children":[{"question":"question","checkboxcount":5,"lower":"a","upper":"b","type":"singlemark"},{"question":"Question","height":4,"expand":true,"type":"textbox"}]},{"heading":"Headline","type":"choicegroup","children":[{"choice":"Choice","type":"groupaddchoice"},{"Question":"question","type":"choiceline","question":"Question"}]},{"question":"question","checkboxcount":5,"lower":"a","upper":"b","type":"singlemark"}]')

        # Create User
        self.testuser = User(username="TestUser",
                             email="test@test.test",
                             is_active=True,
                             is_superuser=True)
        self.password = 'test123'
        self.testuser.set_password(self.password)
        self.testuser.save()

        # Login User
        login = self.client.login(username=self.testuser.username,
                                  password=self.password)
        self.assertEqual(login, True)

        # Create TestSurvey
        self.testsurvey = Survey.objects.create(
            name='test-survey',
            slug=self.testslug,
            title='Test Survey',
            author='The Tester'
            )
        self.testsurvey.owner.add(self.testuser)

    def tearDown(self):
        if os.path.isdir(self.testsurvey.path):
            shutil.rmtree(self.testsurvey.path)

    def test_surveylist_GET(self):
        """Successfully GET survey list"""
        response = self.client.get(self.surveylist_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_surveycreate_GET(self):
        """Successfully GET the survey creation form"""
        response = self.client.get(self.surveycreate_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'survey_create.html')

    def test_surveycreate_POST_no_data(self):
        """Successfully POST the survey creation form without any data"""
        response = self.client.post(self.surveycreate_url)

        self.assertEquals(response.status_code, 200)

    def test_surveyoverview_GET(self):
        """Successfully GET survey overview"""
        response = self.client.get(self.surveyoverview_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'overview.html')

    def test_surveyquestionnairepost_GET(self):
        """Successfully GET questionnaire.json and it is json"""
        testsurvey_instance = Survey.objects.get(slug=self.testsurvey.slug)
        testsurvey_instance.questionnaire = bytes(self.json_questionnaire, 'utf8')
        testsurvey_instance.save()
        response = self.client.get(self.surveyquestionnairepost_url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, testsurvey_instance.questionnaire)
        json.loads(response.content)
        json.loads(testsurvey_instance.questionnaire)

    def test_surveyquestionnairepost_POST(self):
        """Successfully POST the questionnaire draft as json and saving into Survey instance"""
        response = self.client.post(self.surveyquestionnairepost_url, self.json_questionnaire, content_type='application/json')
        testsurvey_instance = Survey.objects.get(slug=self.testsurvey.slug)

        self.assertEquals(testsurvey_instance.questionnaire, bytes(self.json_questionnaire, 'utf8'))
        self.assertEquals(response.status_code, 202)

    def test_surveyquestionnairepost_POST_initialized(self):
        """Wrongly POST the questionnaire draft as json, when survey is already initialized"""
        self.testsurvey.initialized = True
        self.testsurvey.save()
        response = self.client.post(self.surveyquestionnairepost_url, self.json_questionnaire, content_type='application/json')

        self.assertEquals(response.status_code, 404)

    def test_surveydelete_GET(self):
        """Successfully GET survey delete view"""
        response = self.client.get(self.surveydelete_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete.html')

    def test_surveydelete_POST_no_data(self):
        """Successfully POST survey delete view without any data"""
        response = self.client.post(self.surveydelete_url)

        self.assertEquals(response.status_code, 200)

    def test_surveydelete_POST(self):
        """Successfully POST survey delete view to delete survey"""
        response = self.client.post(self.surveydelete_url, {'delete':'YES'})

        self.assertRedirects(response, self.surveylist_url)

class TestPostSurveyInitViews(TestCase):

    def setUp(self):
        if not os.path.isdir(settings.SDAPS_PROJECT_ROOT):
            print('Project root does not exists. Create directory.')
            os.mkdir(settings.SDAPS_PROJECT_ROOT)
        self.client = Client()
        self.testslug = '123ABC'

        # Oriented via matters of "urls.py"
        # upload_matter
        #self.surveyaddimages = reverse('survey_add_images', args=[self.testslug])
        #self.surveyupload = reverse('survey_upload', args=[self.testslug])
        #self.surveyuploadpost = reverse('survey_upload_post', args=[self.testslug])
        #self.surveyuploadfile = reverse('survey_upload_file', args=[self.testslug, 'filename.pdf'])
        # review_matter
        #self.surveyreview = reverse('survey_review', args=[self.testslug])
        #self.surveyreviewsheet = reverse('survey_review_sheet', args=[self.testslug, 1])
        #self.surveyimage = reverse('survey_image', args=[self.testslug, 1])
        # results_matters
        #self.surveyreport = reverse('survey_report', args=[self.testslug])
        #self.reportdownload = reverse('report_download', args=[self.testslug])
        #self.csvdownload = reverse('csv_download', args=[self.testslug])
