# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-05 19:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_manager', '0003_auto_20170702_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='day_created',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2017, 7, 5, 22, 13, 30, 435359)),
        ),
    ]
