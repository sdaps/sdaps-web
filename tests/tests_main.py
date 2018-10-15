import os
import shutil

from django.test import TestCase, tag
from sdaps_ctl.models import Survey
from sdaps_ctl import tasks
from django.contrib.auth.models import User
from django.conf import settings

import datetime

def reset_sdaps_project_root():
    shutil.rmtree(settings.SDAPS_PROJECT_ROOT)
    os.mkdir(settings.SDAPS_PROJECT_ROOT)

class SurveyWithJSONTestCase(TestCase):
    def setUp(self):
        reset_sdaps_project_root()
        User.objects.create(username="admin")
        Survey.objects.create(
                name="Test Uninitialized Survey",
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

    @tag('Survey.create')
    def test_survey_dirs_after_creating(self):
        """After Survey.create(), the survey folder is available in SDAPS_PROJECT_ROOT"""
        test_survey = Survey.objects.get()
        self.assertEqual(os.path.exists(settings.SDAPS_PROJECT_ROOT + "/" + str(test_survey.id)), True)

    @tag('Survey.delete')
    def test_survey_dirs_after_deleting(self):
        """After Survey.delete(), there is no survey folder in SDAPS_PROJECT_ROOT"""
        test_survey = Survey.objects.get()
        self.assertEqual(os.path.exists(settings.SDAPS_PROJECT_ROOT + "/" + str(test_survey.id)), True)
        test_survey_id = test_survey.id
        test_survey.delete()
        self.assertEqual(os.path.exists(settings.SDAPS_PROJECT_ROOT + "/" + str(test_survey_id)), False)
        deleted_date = datetime.datetime.now().strftime('%Y%m%d-%H%M') + "-"
        complete_deleted_path = settings.SDAPS_PROJECT_ROOT + "/deleted/" + deleted_date + str(test_survey_id)
        self.assertEqual(os.path.exists(complete_deleted_path), True)

    @tag('tasks')
    def test_write_questionnaire(self):
        """Questionnaire (JSON) from Survey model gets transformed to a LaTeX document"""
        test_survey = Survey.objects.get()
        texfile = settings.SDAPS_PROJECT_ROOT + "/" + str(test_survey.id) + "/questionnaire.tex"
        if self.assertEqual(tasks.write_questionnaire(test_survey), True):
            self.assertEqual(os.is_file(texfile), True)
