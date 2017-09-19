# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-19 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_initial_tags_resource_types'),
        ('people', '0002_profile_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='attachments',
            field=models.ManyToManyField(to='resources.Attachment'),
        ),
    ]
