
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


class QObject(models.Model):
    #: The survey that this question belongs to
    survey = models.ForeignKey(Survey, db_index=True)

    #: The parent; valid only for some of the question types
    parent = models.ForeignKey('self', related_name='children', db_index=False, null=True, default=None)

    #: The questions text
    text = models.CharField(max_length=300)

    #: The type of the question. This may be one of:
    #:  - heading
    #:  - mark
    #:  - choice
    #:  - markgroup
    #:  - choicegroup
    #:  - textbox
    qtype = models.CharField(max_length=15)

    class Meta:
        order_with_respect_to = 'survey'


class QAnswer(models.Model):
    ANSWER_TYPE_CHOICES = (
        ('check', 'Checkbox'),
        ('text', 'Textbox'),
    )

    #: The question that this answer belongs to
    qobject = models.ForeignKey(QObject, db_index=True)

    #: The text for this answer
    text = models.CharField(max_length=300, choices=ANSWER_TYPE_CHOICES)

    #: The type of this box (either box or textbox)
    btype = models.CharField(max_length=15)

    #: The number of columns to use for this item.
    #: Only valid if the QObject is of type choicegroup.
    columns = models.IntegerField(default=1)

    #: Height of the box. Only valid for textfields.
    height = models.FloatField()

    # And, we want this to be an ordered set.
    class Meta:
        order_with_respect_to = 'qobject'

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

