
from __future__ import absolute_import
from django.conf import settings

from celery import shared_task
from celery.result import AsyncResult
from celery import states

from . import models

from . import utils

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
from sdaps import reporttex
# The cheap way of getting the conversion code ...
from sdaps.cmdline import add

sdaps.init()

defs.latex_preexec_hook = utils.SecureEnv(10)

@shared_task(track_started=True)
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

@shared_task(track_started=True)
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


@shared_task(track_started=True)
def add_and_recognize(survey_id):
    add_images(survey_id)
    recognize(survey_id)


@shared_task
def create_survey(djsurvey):
    # We simply create the directory, the database object
    # and copy the basic LaTeX files

    path = djsurvey.path

    os.mkdir(path)

    # Copy class and dictionary files
    if paths.local_run:
        cls_extra_files = os.path.join(paths.source_dir, 'tex', '*.cls')
        cls_files = os.path.join(paths.source_dir, 'tex', 'class', 'build', 'local', '*.cls')
        tex_files = os.path.join(paths.source_dir, 'tex', 'class', 'build', 'local', '*.tex')
        sty_files = os.path.join(paths.source_dir, 'tex', 'class', 'build', 'local', '*.sty')
        dict_files = os.path.join(paths.build_dir, 'tex', '*.dict')
    else:
        cls_extra_files = None
        cls_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.cls')
        tex_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.tex')
        sty_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.sty')
        dict_files = os.path.join(paths.prefix, 'share', 'sdaps', 'tex', '*.dict')

    def copy_to_survey(files_glob):
        files = glob.glob(files_glob)
        for file in files:
            shutil.copyfile(file, os.path.join(path, os.path.basename(file)))

    if cls_extra_files is not None:
        copy_to_survey(cls_extra_files)
    copy_to_survey(cls_files)
    copy_to_survey(tex_files)
    copy_to_survey(sty_files)
    copy_to_survey(dict_files)

@shared_task(track_started=True)
def write_questionnaire(djsurvey_id):
    from .texwriter import texwriter

    djsurvey = models.Survey.objects.get(id=djsurvey_id)

    # Must not yet be initialized
    assert(djsurvey.initialized == False)

    texwriter(djsurvey)

@shared_task(track_started=True)
def render_questionnaire(djsurvey_id):
    djsurvey = models.Survey.objects.get(id=djsurvey_id)

    # Must not yet be initialized
    assert(djsurvey.initialized == False)

    if utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex'):
        return True
    else:
        return False

@shared_task(track_started=True)
def write_and_render_questionnaire(djsurvey_id):
    write_questionnaire(djsurvey_id)
    render_questionnaire(djsurvey_id)

@shared_task
def build_survey(djsurvey_id):
    """Creates the SDAPS project and database for the survey.
    This process should be run on an already initialized survey that
    has a questionnaire written to it."""

    with models.LockedSurvey(djsurvey_id):
        djsurvey = models.Survey.objects.get(id=djsurvey_id)

        assert(djsurvey.initialized == False)

        import sdaps.setuptex as setup
        from sdaps.utils import latex
        from sdaps.setuptex import sdapsfileparser
        survey = model.survey.Survey.new(djsurvey.path)

        latex.write_override(survey, survey.path('sdaps.opt'), draft=True)
        if not utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex', need_sdaps=True):
            # XXX: The sqlite file should not be created immediately!
            os.unlink(survey.path('survey.sqlite'))
            return False

        # We now have the .sdaps file that can be parsed
        # Defaults
        survey.defs.print_questionnaire_id = False
        survey.defs.print_survey_id = True

        survey.add_questionnaire(model.questionnaire.Questionnaire())

        # Parse qobjects
        try:
            sdapsfileparser.parse(survey)

            for qobject in survey.questionnaire.qobjects:
                qobject.setup.setup()
                qobject.setup.validate()

        except:
            log.error(_("Caught an Exception while parsing the SDAPS file. The current state is:"))
            print(str(survey.questionnaire), file=sys.stderr)
            print("------------------------------------", file=sys.stderr)

            raise

        # Last but not least calculate the survey id
        survey.calculate_survey_id()

        if not survey.check_settings():
            log.error(_("Some combination of options and project properties do not work. Aborted Setup."))
            os.unlink(survey.path('survey.sqlite'))
            return False

        latex.write_override(survey, survey.path('sdaps.opt'), draft=False)

        if not utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex', need_sdaps=True):
            os.unlink(survey.path('survey.sqlite'))
            return False

        survey.save()

        djsurvey.initialized = True
        djsurvey.title = survey.title
        if 'Author' in survey.info:
            djsurvey.author = survey.info['Author']
        djsurvey.save()

        log.logfile.close()

@shared_task
def generate_report(survey_id):
    djsurvey = models.Survey.objects.get(id=survey_id)

    with models.LockedSurvey(djsurvey.id):
        try:
            survey = model.survey.Survey.load(djsurvey.path)

            filename = survey.path('report.pdf')

            # XXX: Don't hardcode to A4, figure out something saner
            reporttex.report(survey, None, filename=filename, papersize="A4")
        finally:
            log.logfile.close()

def queue_generate_report(djsurvey):
    # XXX: Race condition here :-/
    assert not djsurvey.busy

    with models.LockedSurvey(djsurvey.id):
        # And queue a new task
        result = generate_report.apply_async(args=(djsurvey.id, ))

        # Note in DB, that it is queued
        models.ScheduledTasks(celeryid=result.task_id, survey=djsurvey, task='report').save()

def queue_add_and_recognize(djsurvey):
    # XXX: Race condition here :-/
    assert not djsurvey.busy

    with models.LockedSurvey(djsurvey.id):
        # And queue a new task
        result = add_and_recognize.apply_async(args=(djsurvey.id, ))

        # Note in DB, that it is queued
        models.ScheduledTasks(celeryid=result.task_id, survey=djsurvey, task='addrecognize').save()

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

def queue_build_survey(djsurvey):
    # XXX: Race condition here :-/
    assert not djsurvey.busy

    with models.LockedSurvey(djsurvey.id):
        # And queue a new task
        result = build_survey.apply_async(args=(djsurvey.id, ))

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

