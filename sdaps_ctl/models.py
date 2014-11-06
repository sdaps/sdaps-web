
import os
import time

from django.db.models import signals
from django.db import models

from django.conf import settings

class Survey(models.Model):

    name = models.CharField(max_length=100, unique=True)
    directory = models.CharField(max_length=110)

    #: Whether a process has the internal SDAPS database locked
    locked = models.BooleanField(default=False)

    #: Whether the project is initilized (and the questionnaire cannot be
    #: modified anymore).
    initialized = models.BooleanField(default=False)

    # (cached) properties of this survey

    # These IDs may *not* be unique.
    surveyid = models.PositiveIntegerField(default=0)
    globalid = models.CharField(max_length=40, default='')

    title = models.CharField(max_length=200, default='')
    author = models.CharField(max_length=200, default='')

    questionnaire = models.TextField(default='[]')


    # Still to do:
    #  * Permission handling?
    #  * ...

    @property
    def path(self):
        return os.path.join(settings.SDAPS_PROJECT_ROOT, self.directory)


class LockedSurvey(object):
    def __init__(self, surveyid):
        self.surveyid = surveyid

    def __enter__(self):
        locked = False
        while not locked:
            count = Survey.objects.filter(id=self.surveyid, locked=False).update(locked=True)
            if count == 1:
                locked = True
            else:
                # Sleep ...
                time.sleep(0.1)

    def __exit__(self, type, value, traceback):
        s = Survey.objects.filter(id=self.surveyid).update(locked=False)


class ScheduledTasks(models.Model):

    #: The survey that this task belongs to
    survey = models.ForeignKey(Survey, db_index=True, related_name="tasks")

    #: The type of the task
    task = models.CharField(max_length=10, db_index=True)

    #: The celery identifier of the queued task
    celeryid = models.CharField(max_length=200)

    class Meta:
        unique_together = (('survey','task'),)


# ---------------------------------------------------------

def move_survey_dir(sender, instance, using, **kwargs):
    u"""This signal handler moves the project directory into the "deleted"
    directory whenever a survey is removed from the database."""

    dirname = instance.directory
    path = instance.path

    if dirname and os.path.isdir(path):
        delpath = os.path.join(settings.SDAPS_PROJECT_ROOT, 'deleted')

        # Make sure the "deleted" directory exists
        if not os.path.isdir(delpath):
            os.mkdir(delpath)

        # And rename/move the old directory
        os.rename(path, os.path.join(delpath, dirname))

signals.post_delete.connect(move_survey_dir, sender=Survey)

