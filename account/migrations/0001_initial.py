# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 05:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CostumerAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='Ονομα')),
                ('last_name', models.CharField(max_length=100, verbose_name='Επίθετο')),
                ('shipping_address_1', models.CharField(blank=True, max_length=100, null=True, verbose_name='Διεύθυνση Αποστολής')),
                ('shipping_city', models.CharField(blank=True, max_length=50, null=True, verbose_name='Πόλη')),
                ('shipping_zip_code', models.IntegerField(blank=True, null=True, verbose_name='Ταχυδρομικός Κώδικας')),
                ('billing_name', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_address', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_city', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_zip_code', models.IntegerField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=10, verbose_name='Τηλέφωνο')),
                ('phone1', models.CharField(blank=True, max_length=10, verbose_name='Τηλέφωνο')),
                ('cellphone', models.CharField(blank=True, max_length=10, verbose_name='Κινητό')),
                ('fax', models.CharField(blank=True, max_length=10, verbose_name='Fax')),
                ('is_retail', models.BooleanField(default=True)),
                ('is_eshop', models.BooleanField(default=True)),
                ('afm', models.CharField(blank=True, max_length=9, verbose_name='ΑΦΜ')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Υπόλοιπο')),
                ('paid_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('total_order_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Χρεωστικό Υπόλοιπο')),
            ],
        ),
    ]
