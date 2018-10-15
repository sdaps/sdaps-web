
import os
import time
import datetime

from . import tasks

from django.db.models import signals
from django.db import models

from django.conf import settings

from django.contrib.auth.models import User, Group
from django.utils.text import get_valid_filename

from django.urls import reverse

from celery.result import AsyncResult


class Survey(models.Model):

    class Meta:
        permissions = (("review_survey", "Can review surveys"),)

    name = models.CharField(max_length=100)

    #: Whether the project is initilized (and the questionnaire cannot be
    #: modified anymore).
    initialized = models.BooleanField(default=False)

    # (cached) properties of this survey

    # These IDs may *not* be unique.
    surveyid = models.PositiveIntegerField(default=0)
    globalid = models.CharField(max_length=40, default='', blank=True)

    title = models.CharField(max_length=200, default='')
    author = models.CharField(max_length=200, default='')

    questionnaire = models.BinaryField(default=b'[]')

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)

    @property
    def path(self):
        return os.path.join(settings.SDAPS_PROJECT_ROOT, str(self.id))

UPLOADING = 0
FINISHED = 1
ERROR = 2
UPLOAD_STATUS = (
    (UPLOADING, "Uploading"),
    (FINISHED, "Finished"),
    (ERROR, "Error"),
)

class UploadedFile(models.Model):

    #: The survey that this file belongs to
    survey = models.ForeignKey(Survey, db_index=True, related_name="uploads", on_delete=models.CASCADE)

    def generate_filename(instance, filename):
        filename = get_valid_filename(instance.filename)
        return os.path.join(instance.survey.path, 'uploads', '%i-%s' % (instance.id, filename))

    file = models.FileField(max_length=255, editable=False, upload_to=generate_filename, storage=settings.SDAPS_UPLOAD_STORAGE)
    #del generate_filename

    filename = models.CharField(max_length=255)
    filesize = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True)

    status = models.PositiveSmallIntegerField(choices=UPLOAD_STATUS,
                                              default=UPLOADING)

    def get_description(self):
        size = self.file.size

        url = reverse('survey_upload_file', args=(self.survey.id, self.filename))

        res = {
            'name' : self.filename,
            'offset' : size,
            'size' : self.filesize,
            'url' : url,
            'deleteUrl' : url,
            'deleteType' : 'DELETE',
        }

        if self.status == ERROR:
            res['error'] = 'Upload was not successful.'

        return res

    def append_chunk(self, data, offset, length):
        assert offset == self.file.size

        data = data.read()
        assert length is None or len(data) == length

        f = open(self.file.name, mode='ab')
        #self.file.open(mode='ab')
        #self.file.write(data)
        #self.file.close()
        f.write(data)
        f.close()

        size = self.file.size
        if size >= self.filesize:
            if self.filesize != size:
                self.status = ERROR
            else:
                self.status = FINISHED

        self.save()

# ---------------------------------------------------------

def create_survey_dir(sender, instance, created, **kwargs):
    if not created:
        return

    tasks.create_survey(instance)

def move_survey_dir(sender, instance, using, **kwargs):
    """This signal handler moves the project directory into the "deleted"
    directory whenever a survey is removed from the database."""

    path = instance.path

    if path and os.path.isdir(path):
        delpath = os.path.join(settings.SDAPS_PROJECT_ROOT, 'deleted')

        # Make sure the "deleted" directory exists
        if not os.path.isdir(delpath):
            os.mkdir(delpath)

        # And rename/move the old directory
        os.rename(path, os.path.join(delpath, datetime.datetime.now().strftime('%Y%m%d-%H%M') + '-' + str(instance.id)))

signals.post_save.connect(create_survey_dir, sender=Survey)
signals.post_delete.connect(move_survey_dir, sender=Survey)

def delete_uploaded_file(sender, instance, using, **kwargs):
    instance.file.delete(save=False)

signals.post_delete.connect(delete_uploaded_file, sender=UploadedFile)

