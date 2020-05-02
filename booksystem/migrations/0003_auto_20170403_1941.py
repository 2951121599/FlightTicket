# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-03 19:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booksystem', '0002_auto_20170402_2346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='user',
        ),
        migrations.AddField(
            model_name='flight',
            name='user',
            field=models.ManyToManyField(default=1, to=settings.AUTH_USER_MODEL),
        ),
    ]