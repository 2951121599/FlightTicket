# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-04-18 10:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booksystem', '0007_userinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='score',
            field=models.CharField(default=0, max_length=50, verbose_name='积分'),
        ),
    ]
