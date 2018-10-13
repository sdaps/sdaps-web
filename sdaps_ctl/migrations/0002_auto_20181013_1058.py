# Generated by Django 2.1.2 on 2018-10-13 10:58

import django.core.files.storage
from django.db import migrations, models
import sdaps_ctl.models


class Migration(migrations.Migration):

    dependencies = [
        ('sdaps_ctl', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='scheduledtasks',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='scheduledtasks',
            name='survey',
        ),
        migrations.AlterField(
            model_name='survey',
            name='questionnaire',
            field=models.BinaryField(default=b'[]'),
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(editable=False, max_length=255, storage=django.core.files.storage.FileSystemStorage('/home/dennis/Projekte/sdaps_web/proj', base_url=None), upload_to=sdaps_ctl.models.UploadedFile.generate_filename),
        ),
        migrations.DeleteModel(
            name='ScheduledTasks',
        ),
    ]
