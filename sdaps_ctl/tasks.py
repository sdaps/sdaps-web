
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
from sdaps import log
from sdaps import model
from sdaps import defs
from sdaps import paths
# The cheap way of getting the conversion code ...
from sdaps.cmdline import add

sdaps.init()

defs.latex_preexec_hook = utils.SecureEnv(10)

@task()
def add_images(survey_id):
    survey = models.Survey.objects.get(id=survey_id)

    with models.LockedSurvey(survey.id):
        images = list(survey.uploads.all())
        filenames = []
        for image in images:
            if image.status != models.FINISHED:
                continue

            filenames.append(image.file.name)

        # Nothing to do ...
        if not filenames:
            return

        cmdline = {
            'images' : filenames,
            'convert' : True,
            'transform' : False, # XXX
            'force' : False,
            'copy' : True,
            'duplex' : False, # XXX
            'project' : survey.path
        }

        # TODO: Need error reporting (exception)!
        try:
            error = add.add(cmdline)
        finally:
            log.logfile.close()

        if not error:
            # Remove the added files from the database
            for image in images:
                image.delete()

        else:
            # TODO: Need error reporting!
            raise AssertionError("Error adding files!")

@task()
def recognize(djsurvey_id):
    from sdaps.recognize import recognize

    djsurvey = models.Survey.objects.get(id=djsurvey_id)

    with models.LockedSurvey(djsurvey.id):
        try:
            survey = model.survey.Survey.load(djsurvey.path)

            filter = lambda : not (survey.sheet.verified or survey.sheet.recognized)

            recognize(survey, filter)
        finally:
            log.logfile.close()


@task()
def add_and_recognize(survey_id):
    add_images(survey_id)
    recognize(survey_id)

def queue_add_and_recognize(djsurvey):
    # XXX: Race condition here :-/
    assert not djsurvey.busy

    with models.LockedSurvey(djsurvey.id):
        # And queue a new task
        result = add_and_recognize.apply_async(args=(djsurvey.id, ), queue="background")

        # Note in DB, that it is queued
        models.ScheduledTasks(celeryid=result.task_id, survey=djsurvey, task='addrecognize').save()



@task()
def create_survey(djsurvey):
    # We simply create the directory, the database object
    # and copy the basic LaTeX files

    path = djsurvey.path

    os.mkdir(path)

    # Copy class and dictionary files
    if paths.local_run:
        cls_file = os.path.join(paths.source_dir, 'tex', 'sdaps.cls')
        code128_file = os.path.join(paths.source_dir, 'tex', 'code128.tex')
        qrcode_file = os.path.join(paths.source_dir, 'tex', 'qrcode.sty')
        dict_files = os.path.join(paths.build_dir, 'tex', '*.dict')
        dict_files = glob.glob(dict_files)
    else:
        cls_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'sdaps.cls')
        code128_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'code128.tex')
        qrcode_file = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', 'qrcode.sty')
        dict_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.dict')
        dict_files = glob.glob(dict_files)

    shutil.copyfile(cls_file, os.path.join(path, 'sdaps.cls'))
    shutil.copyfile(code128_file, os.path.join(path, 'code128.tex'))
    shutil.copyfile(qrcode_file, os.path.join(path, 'qrcode.sty'))
    for dict_file in dict_files:
        shutil.copyfile(dict_file, os.path.join(path, os.path.basename(dict_file)))

@task()
def write_questionnaire(djsurvey_id):
    from texwriter import texwriter

    djsurvey = models.Survey.objects.get(id=djsurvey_id)
    texwriter(djsurvey)

@task()
def render_questionnaire(djsurvey_id):
    djsurvey = models.Survey.objects.get(id=djsurvey_id)

    # Must not yet be initialized
    assert(djsurvey.initialized == False)

    if utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex'):
        return True
    else:
        return False

@task
def write_and_render_questionnaire(djsurvey_id):
    write_questionnaire(djsurvey_id)
    render_questionnaire(djsurvey_id)

def queue_timed_write_and_render(djsurvey):
    with models.LockedSurvey(djsurvey.id):
        try:
            task = models.ScheduledTasks.objects.get(survey=djsurvey, task='render')

            # Will the task still run?
            if AsyncResult(task.celeryid).state in [states.PENDING, states.RETRY]:
                return

            # Seems like the task will not run, so remove the old one
            task.delete()
        except models.ScheduledTasks.DoesNotExist:
            pass

        # And queue a new task
        result = write_and_render_questionnaire.apply_async(args=(djsurvey.id, ), countdown=1)

        # Note in DB, that it is queued
        models.ScheduledTasks(celeryid=result.task_id, survey=djsurvey, task='render').save()

@task()
def build_survey(djsurvey_id):
    """Creates the SDAPS project and database for the survey.
    This process should be run on an already initialized survey that
    has a questionnaire written to it."""

    with models.LockedSurvey(djsurvey_id):
        djsurvey = models.Survey.objects.get(id=djsurvey_id)

        assert(djsurvey.initialized == False)

        import sdaps.setuptex as setup
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

        setup.write_latex_override_file(survey)

        if not utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex', need_sdaps=True):
            return False

        survey.save()

        djsurvey.initialized = True
        djsurvey.title = survey.title
        if 'Author' in survey.info:
            djsurvey.author = survey.info['Author']
        djsurvey.save()

        log.logfile.close()

def queue_build_survey(djsurvey):
    # XXX: Race condition here :-/
    assert not djsurvey.busy

    with models.LockedSurvey(djsurvey.id):
        # And queue a new task
        result = build_survey.apply_async(args=(djsurvey.id, ), queue="background")

        # Note in DB, that it is queued
        models.ScheduledTasks(celeryid=result.task_id, survey=djsurvey, task='build').save()


def get_tasks(djsurvey):
    result = list()
    try:
        for task in models.ScheduledTasks.objects.filter(survey=djsurvey).all():
            # Prune any tasks that are done or resulted in an error.
            if not AsyncResult(task.celeryid).state in [states.PENDING, states.RETRY]:
                task.delete()
            else:
                result.append(task)

        return result

    except models.ScheduledTasks.DoesNotExist:
        return []

