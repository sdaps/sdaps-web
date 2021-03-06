# Generated by Django 2.2.16 on 2020-10-27 10:56

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import sdaps_ctl.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=100)),
                ('initialized', models.BooleanField(default=False)),
                ('surveyid', models.PositiveIntegerField(default=0)),
                ('globalid', models.CharField(blank=True, default='', max_length=40)),
                ('title', models.CharField(default='', max_length=200)),
                ('author', models.CharField(default='', max_length=200)),
                ('language', models.CharField(default='', max_length=200)),
                ('latex_class_options', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('questionnaire', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('owner', models.ManyToManyField(related_name='ownership_of_survey', related_query_name='ownership_of_survey', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_design_draft', 'Can design a survey draft via the editor'), ('can_initialize', 'Can finally setup/initialize the survey for printing'), ('can_download_empty', 'Can download empty (to be filled) survey)'), ('can_upload_scans', 'Can upload scanned sheets'), ('can_review_scans', 'Can review uploaded scanned sheets'), ('can_verify_scans', 'Can verify uploaded reviewed scans per page'), ('can_download_results', 'Can download report and csv files'), ('can_download_scans', 'Can download uploaded scanned sheets'), ('can_download_project', 'Can download the whole sdaps project for backup or working locally'), ('can_edit_basic_info', 'Can edit for example title, author, global id...')),
                'default_permissions': ('add', 'change', 'delete'),
            },
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(editable=False, max_length=255, storage=django.core.files.storage.FileSystemStorage('/tmp/projects', base_url=None), upload_to=sdaps_ctl.models.UploadedFile.generate_filename)),
                ('filename', models.CharField(max_length=255)),
                ('filesize', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Uploading'), (1, 'Finished'), (2, 'Error')], default=0)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploads', to='sdaps_ctl.Survey')),
            ],
        ),
    ]
