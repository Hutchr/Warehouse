# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 05:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('mysite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='footercategory',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.CategorySite', unique=True),
        ),
        migrations.AddField(
            model_name='footer',
            name='page_related',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mysite.WelcomePage'),
        ),
        migrations.AddField(
            model_name='footer',
            name='pick_category_1',
            field=models.ManyToManyField(blank=True, null=True, to='products.CategorySite'),
        ),
        migrations.AddField(
            model_name='banners',
            name='page_related',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mysite.WelcomePage'),
        ),
    ]
