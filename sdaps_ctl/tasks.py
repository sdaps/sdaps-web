
from django.conf import settings

from celery.task import task
from celery.result import AsyncResult
from celery import states

import models

import utils

import sys
import os
import re
import shutil
import glob

import sdaps
from sdaps import model
from sdaps import defs
from sdaps import paths

sdaps.init()

@task()
def add(x, y):
    return x + y

@task()
def add_scan(project, image_file):
    from sdaps import add
    # TODO

@task()
def recognize(djsurvey):
    from sdaps.recognize.recognize import recognize

    survey = model.survey.Survey.load(djsurvey.directory)

    recognize(survey)

@task()
def initialize_survey(name):
    # We simply create the directory, the database object
    # and copy the basic LaTeX files
    s = models.Survey()
    s.name = name
    s.directory = ''

    s.save()
    path = None

    try:
        # Mangle the name to create a nice path name
        mangled_name = name.replace(' ', '_')
        mangled_name, count = re.subn('[^a-zA-Z0-9_]', '', mangled_name)

        s.directory = "%i-%s" % (s.id, mangled_name)

        os.mkdir(s.path)

        # Copy class and dictionary files
        if paths.local_run:
            cls_file = os.path.join(paths.source_dir, 'tex', 'sdaps.cls')
            code128_file = os.path.join(paths.source_dir, 'tex', 'code128.tex')
            dict_files = os.path.join(paths.build_dir, 'tex', '*.dict')
            dict_files = glob.glob(dict_files)
        else:
            cls_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'sdaps.cls')
            code128_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'code128.tex')
            dict_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.dict')
            dict_files = glob.glob(dict_files)

        shutil.copyfile(cls_file, os.path.join(s.path, 'sdaps.cls'))
        shutil.copyfile(code128_file, os.path.join(s.path, 'code128.tex'))
        for dict_file in dict_files:
            shutil.copyfile(dict_file, os.path.join(s.path, os.path.basename(dict_file)))

        s.save()

    except Exception, e:
        s.delete()

        raise e

    return s

@task()
def write_questionnaire(djsurvey):
    from texwriter import texwriter

    texwriter(djsurvey)

@task()
def render_questionnaire(djsurvey):
    # Must not yet be initialized
    assert(djsurvey.initialized == False)

    if utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex'):
        return True
    else:
        return False

@task
def write_and_render_questionnaire(djsurvey):
    write_questionnaire(djsurvey)
    render_questionnaire(djsurvey)

def queue_timed_write_and_render(djsurvey):
    with models.LockedSurvey(djsurvey.id):
        try:
            task = models.ScheduledTasks.objects.get(survey=djsurvey, task='render')

            # Will the task still run?
            if AsyncResult(task.celeryid).state in [states.PENDING, states.RETRY]:
                print "not queuing task!!!!"
                return

            # Seems like the task will not run, so remove the old one
            task.delete()
        except models.ScheduledTasks.DoesNotExist:
            pass

        print "queueing task"
        # And queue a new task
        result = write_and_render_questionnaire.apply_async(args=(djsurvey, ),countdown=1)

        # Note in DB, that it is queued
        models.ScheduledTasks(celeryid=result.task_id, survey=djsurvey, task='render').save()

@task()
def build_survey(djsurvey):
    """Creates the SDAPS project and database for the survey.
    This process should be run on an already initialized survey that
    has a questionnaire written to it."""

    with models.LockedSurvey(djsurvey.id):
        assert(djsurvey.initialized == False)

        from sdaps.setuptex import setup
        from sdaps.setuptex import sdapsfileparser
        survey = model.survey.Survey.new(djsurvey.path)

        setup.write_latex_override_file(survey, draft=True)
        if not utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex', need_sdaps=True):
            return False

        # We now have the .sdaps file that can be parsed
        # Defaults
        survey.defs.print_questionnaire_id = False
        survey.defs.print_survey_id = True

        survey.add_questionnaire(model.questionnaire.Questionnaire())

        # Parse qobjects
        try:
            sdapsfileparser.parse(survey)
        except Exception, e:
            sys.stderr.write("Caught an Exception while parsing the SDAPS file. The current state is:")
            sys.stderr.write(unicode(survey.questionnaire))
            sys.stderr.write("\n------------------------------------\n")

            raise e

        # Last but not least calculate the survey id
        survey.calculate_survey_id()

        if not survey.check_settings():
            sys.stderr.write(_("Some combination of options and project properties do not work. Aborted Setup."))
            shutil.rmtree(survey.path())
            return 1

        setup.write_latex_override_file(survey, draft=True)

        if not utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex', need_sdaps=True):
            return False

        survey.save()

        djsurvey.initialized = True
        djsurvey.title = survey.title
        if 'Author' in survey.info:
            djsurvey.author = survey.info['Author']
        djsurvey.save()

