# Generated by Django 2.1.7 on 2019-07-15 19:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sdaps_ctl', '0005_auto_20190707_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
