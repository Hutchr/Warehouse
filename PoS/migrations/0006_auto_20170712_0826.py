# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-12 05:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PoS', '0005_auto_20170710_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailorder',
            name='day_created',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 12, 8, 26, 22, 984781)),
        ),
    ]