# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-04-18 18:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booksystem', '0008_userinfo_score'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userinfo',
            options={'verbose_name': '用户信息表', 'verbose_name_plural': '用户信息表'},
        ),
        migrations.AddField(
            model_name='userinfo',
            name='kind',
            field=models.CharField(default='低价值用户', max_length=50, verbose_name='分类'),
        ),
        migrations.AlterModelTable(
            name='userinfo',
            table='user_info',
        ),
    ]
