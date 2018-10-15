
from __future__ import absolute_import
from django.conf import settings
from django.core.cache import cache

from celery import shared_task
from celery.result import AsyncResult
from celery import states
from celery.five import monotonic
from celery.utils.log import get_task_logger
from contextlib import contextmanager

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

logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 20

sdaps.init(local_run=True)

defs.latex_preexec_hook = utils.SecureEnv(10)

# task_lock() makes sure that tasks are not running in parallel, based on a
# lock_id that's get recognized
@contextmanager
def task_lock(lock_id, oid):
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)

@shared_task(track_started=True, bind=True)
def add_images(self, djsurvey):

    lock_id = ('%s_add_images' % djsurvey.id)
    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            images = list(djsurvey.uploads.all())
            filenames = []
            for image in images:
                if image.status != models.FINISHED:
                    continue

                filenames.append(image.file.name)

            # Nothing to do ...
            if not filenames:
                print("No files to add")
                return

            cmdline = {
                'images' : filenames,
                'convert' : True,
                'transform' : False, # XXX
                'force' : False,
                'copy' : True,
                'duplex' : False, # XXX
                'project' : djsurvey.path
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
                logger.debug('Uploaded image files got deleted')
                return True
            else:
                # TODO: Need error reporting!
                raise AssertionError("Error adding files!")
                return False
        else:
            return False

@shared_task(track_started=True, bind=True)
def recognize_scan(self, djsurvey):
    from sdaps.recognize import recognize

    lock_id = ('%s_recognize' % djsurvey.id)
    print(lock_id)
    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            survey = model.survey.Survey.load(djsurvey.path)

            filter = lambda : not (survey.sheet.verified or survey.sheet.recognized)

            recognize(survey, filter)
            log.logfile.close()

@shared_task(bind=True)
def create_survey(self, djsurvey):
    lock_id = ('%s_create_survey' % djsurvey.id)
    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
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

@shared_task(track_started=True, bind=True)
def write_questionnaire(self, djsurvey):
    """Translates the json file of questionnaire objects to LaTeX commands."""
    from .texwriter import texwriter

    lock_id = ('%s_write_questionnaire' % djsurvey.id)
    logger.debug('Write questionnaire (with id %s)', djsurvey.id)
    # Must not yet be initialized
    assert(djsurvey.initialized == False)

    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            texwriter(djsurvey)
            logger.debug('Questionnaire written (with id %s)', djsurvey.id)
            return True
        else:
            return False

@shared_task(track_started=True, bind=True)
def render_questionnaire(self, djsurvey):
    """Renders the LaTeX questionnaire out of the json file that was send and
    saved via the editor by users"""
    lock_id = ('%s_render_questionnaire' % djsurvey.id)
    logger.debug('Render questionnaire (with id %s)', djsurvey.id)
    # Must not yet be initialized
    assert(djsurvey.initialized == False)

    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            if utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex'):
                logger.debug('Render successful (with id %s)', djsurvey.id)
                return True
            else:
                logger.debug('Render failed (with id %s)', djsurvey.id)
                return False
    logger.debug('Render task (with id %s) is already running. It will be automaticly deleted after %s minutes' % (djsurvey.id, (LOCK_EXPIRE/60)))
    return False

@shared_task(bind=True)
def build_survey(self, djsurvey):
    """Creates the SDAPS project and database for the survey.
    This process should be run on an already initialized survey that
    has a questionnaire written to it."""
    lock_id = ('%s_build_survey' % djsurvey.id)
    assert(djsurvey.initialized == False)

    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
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
                log.error("Caught an Exception while parsing the SDAPS file. The current state is:")
                print(str(survey.questionnaire), file=sys.stderr)
                print("------------------------------------", file=sys.stderr)

                raise AssertionError("Exception while parsing the SDAPS file.")

            # Last but not least calculate the survey id
            survey.calculate_survey_id()

            if not survey.check_settings():
                log.error("Some combination of options and project properties do not work. Aborted Setup.")
                os.unlink(survey.path('survey.sqlite'))
                return False

            latex.write_override(survey, survey.path('sdaps.opt'), draft=False)

            if not utils.atomic_latex_compile(djsurvey.path, 'questionnaire.tex', need_sdaps=True):
                os.unlink(survey.path('survey.sqlite'))
                return False
            # TODO: If something goes wrong while initializing the survey,
            # there should be an option to delete the files.
            survey.save()

            djsurvey.initialized = True
            djsurvey.title = survey.title
            if 'Author' in survey.info:
                djsurvey.author = survey.info['Author']
            djsurvey.save()

            log.logfile.close()

@shared_task(bind=True)
def generate_report(self, djsurvey):
    lock_id = ('%s_generate_report' % djsurvey.id)

    with task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            survey = model.survey.Survey.load(djsurvey.path)

            filename = survey.path('report.pdf')

            # XXX: Don't hardcode to A4, figure out something saner
            reporttex.report(survey, None, filename=filename, papersize="A4")
            log.logfile.close()

