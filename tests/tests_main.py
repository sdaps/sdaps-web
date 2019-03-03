import os
import shutil

from django.test import TestCase, tag
from sdaps_ctl.models import Survey
from sdaps_ctl import tasks
from sdaps_web import settings
from django.contrib.auth.models import User
from django.conf import settings

import datetime

def reset_sdaps_project_root():
    shutil.rmtree(settings.SDAPS_PROJECT_ROOT)
    os.mkdir(settings.SDAPS_PROJECT_ROOT)

class SurveyModelFunctionsTestCase(TestCase):
    '''The SurveyModel has a lot of functions directly attached to it, like
    "create()" or "delete()"'''
    def setUp(self):
        reset_sdaps_project_root()
        self.testslug = '123ABC'
        self.testuser = User.objects.create(username="admin")
        self.testsurvey = Survey.objects.create(
                name="Test Survey Model Functions",
                slug=self.testslug,
                title="Test Survey Title",
                author="Mrs. and Mr. Surveycreator",
                questionnaire=b"""
                [
                  {
                    "title": "Title",
                    "type": "section"
                  },
                  {
                    "heading": "Headline",
                    "checkboxcount": 5,
                    "type": "markgroup",
                    "children": [
                      {
                        "question": "Question",
                        "lower": "a",
                        "upper": "b",
                        "type": "markline"
                      },
                      {
                        "question": "Question2",
                        "lower": "a",
                        "upper": "b",
                        "type": "markline"
                      }
                    ]
                  }
                ]
                """,
                owner=User.objects.get(username="admin"))

    def tearDown(self):
        if os.path.isdir(self.testsurvey.path):
            shutil.rmtree(self.testsurvey.path)

    @tag('Survey.create')
    def test_survey_dirs_after_creating(self):
        """Checks if after Survey.create(), the survey folder is available in SDAPS_PROJECT_ROOT"""
        self.testsurvey_instance = Survey.objects.get(slug=self.testslug)
        self.assertTrue(os.path.exists(settings.SDAPS_PROJECT_ROOT + "/" + str(self.testsurvey_instance.id)))

    @tag('Survey.delete')
    def test_survey_dirs_after_deleting(self):
        """Checks if after Survey.delete(), there is no survey folder in SDAPS_PROJECT_ROOT"""
        self.testsurvey_instance = Survey.objects.get(slug=self.testslug)
        deleted_datetime = datetime.datetime.now().strftime('%Y%m%d-%H%M') + "-"
        complete_deleted_path = settings.SDAPS_PROJECT_ROOT + "/deleted/" + deleted_datetime + str(self.testsurvey_instance.id)
        self.testsurvey_instance.delete()

        self.assertEqual(os.path.exists(settings.SDAPS_PROJECT_ROOT + "/" + str(self.testsurvey_instance.id)), False)
        self.assertTrue(os.path.exists(complete_deleted_path))


class UninitializedSurveyTasksTestCase(TestCase):
    '''The survey gets initialized, when the questionnaire is ready for print.'''

    def setUp(self):
        reset_sdaps_project_root()
        if not os.path.isdir(settings.SDAPS_PROJECT_ROOT):
            print('Project root does not exists. Create directory.')
            os.mkdir(settings.SDAPS_PROJECT_ROOT)
        self.testuser = User.objects.create(username="admin")
        self.testslug = '123ABC'
        self.testsurvey = Survey.objects.create(
                name="Test Uninitialized Survey",
                slug=self.testslug,
                title="Test Survey Title",
                author="Mrs. and Mr. Surveycreator",
                questionnaire=bytes('[{"columns":2,"type":"multicol","children":[{"text":"Text","type":"textbody"},{"text":"Text","type":"textbody"}]},{"question":"Question","height":4,"expand":true,"type":"textbox"},{"title":"Section","type":"section"},{"text":"Text","type":"textbody"},{"question":"question","checkboxcount":5,"lower":"a","upper":"b","type":"singlemark"},{"question":"Question","columns":4,"type":"choicequestion","children":[{"answer":"Item","colspan":1,"type":"choiceitem"},{"answer":"Item","colspan":2,"height":1.2,"type":"choiceitemtext"},{"answer":"Item2","colspan":2,"height":1.2,"type":"choiceitemtext"}]},{"question":"Question","height":4,"expand":true,"type":"textbox"},{"heading":"Headline","checkboxcount":5,"type":"markgroup","children":[{"question":"Question","lower":"a","upper":"b","type":"markline"},{"question":"Question","lower":"a","upper":"b","type":"markline"}]},{"title":"Title","type":"section"},{"heading":"Headline","type":"choicegroup","children":[{"choice":"Choice","type":"groupaddchoice"},{"Question":"question","type":"choiceline","question":"ONE"},{"Question":"question","type":"choiceline","question":"Two"},{"Question":"question","type":"choiceline","question":"Three"}]}]', 'utf8'),
                owner=User.objects.get(username="admin"))

    def tearDown(self):
        if os.path.isdir(self.testsurvey.path):
            shutil.rmtree(self.testsurvey.path)

    @tag('tasks')
    def test_write_questionnaire(self):
        """Checks if questionnaire (JSON) from Survey model gets transformed to a LaTeX document"""
        self.testsurvey_instance = Survey.objects.get(slug=self.testslug)
        texfile = self.testsurvey_instance.path + "/questionnaire.tex"
        if self.assertTrue(tasks.write_questionnaire(self.testsurvey_instance.id)):
            self.assertTrue(os.path.isfile(texfile))