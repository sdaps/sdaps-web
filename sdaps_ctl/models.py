#!/usr/bin/env python3
# sdaps_web - Webinterface for SDAPS
# Copyright(C) 2019, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os
import time
import datetime
import json

from . import tasks

from django.db.models import signals
from django.db import models

from django.conf import settings

from django.contrib.auth.models import User, Group
from django.utils.text import get_valid_filename
from django.utils.crypto import get_random_string

from django.urls import reverse

from celery.result import AsyncResult
from guardian.shortcuts import assign_perm, get_perms_for_model

class Survey(models.Model):

    class Meta:
        permissions = (
                ("can_design_draft", "Can design a survey draft via the editor"),
                ("can_initialize", "Can finally setup/initialize the survey for printing"),
                ("can_download_empty", "Can download empty (to be filled) survey)"),
                ("can_upload_scans", "Can upload scanned sheets"),
                ("can_review_scans", "Can review uploaded scanned sheets"),
                ("can_verify_scans", "Can verify uploaded reviewed scans per page"),
                ("can_download_results", "Can download report and csv files"),
                ("can_download_scans", "Can download uploaded scanned sheets"),
                ("can_download_project", "Can download the whole sdaps project for backup or working locally"),
                ("can_edit_basic_info", "Can edit for example title, author, global id..."),
                )
        default_permissions = ('add', 'change', 'delete')

    slug = models.SlugField(unique=True)
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
    language = models.CharField(max_length=200, default='')
    latex_class_options = models.TextField(default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    questionnaire = models.BinaryField(default=b'[]')

    owner = models.ManyToManyField(
            User,
            related_name="ownership_of_survey",
            related_query_name="ownership_of_survey"
            )

    @property
    def path(self):
        return os.path.join(settings.SDAPS_PROJECT_ROOT, str(self.id))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(6,'ABCDEFGHIJKLMNOPQVWXYZ0123456789')
        super().save(*args, **kwargs)

    def get_tex_cls_opts(self, key):
        if self.latex_class_options:
            tex_cls_opts = json.loads(self.latex_class_options)
            return tex_cls_opts[key]
        else:
            return False

    def set_tex_cls_opts(self, key, value):
        # change an option
        tex_cls_opts_json = json.loads('{}')
        if self.latex_class_options:
            tex_cls_opts_json = json.loads(self.latex_class_options)
        # create the option
        tex_cls_opts_json[key] = value
        self.latex_class_options = json.dumps(tex_cls_opts_json)
        self.save()
    
    @property
    def opts_noinfo(self):
        return self.get_tex_cls_opts('noinfo')

    @property
    def opts_paper_format(self):
        return self.get_tex_cls_opts('paper_format')

    @property
    def opts_print_questionnaire_id(self):
        return self.get_tex_cls_opts('print_questionnaire_id')

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

        url = reverse('survey_upload_scans_file', args=(self.survey.slug, self.filename))

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

def assign_initial_survey_perms(sender, instance, created, **kwargs):
    survey_model_perms = [perm.codename for perm in get_perms_for_model(sender)]
    for model_perm in survey_model_perms:
        for owner in instance.owner.all():
            assign_perm(model_perm, owner, instance)

signals.post_save.connect(assign_initial_survey_perms, sender=Survey)
signals.post_save.connect(create_survey_dir, sender=Survey)
signals.post_delete.connect(move_survey_dir, sender=Survey)

def delete_uploaded_file(sender, instance, using, **kwargs):
    instance.file.delete(save=False)

signals.post_delete.connect(delete_uploaded_file, sender=UploadedFile)

