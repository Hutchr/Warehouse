# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 05:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(max_length=50)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('qty', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('is_ordered', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['date_added'],
            },
            managers=[
                ('my_query', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='CartOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(max_length=50)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_ordered', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CartRules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=100)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=2, max_digits=5)),
                ('shipping_cost_limit', models.DecimalField(decimal_places=2, default=35, max_digits=5, verbose_name='Όριο Αξίας Μεταφορικών')),
                ('cash_on_delivery_cost', models.DecimalField(decimal_places=2, default=2, max_digits=5)),
                ('cash_on_delivery_limit', models.DecimalField(decimal_places=2, default=20, max_digits=5, verbose_name='Όριο Αξίας Μεταφορικών')),
            ],
            options={
                'verbose_name_plural': '1. Κανόνες Καλαθιού',
            },
        ),
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=100)),
                ('coupon_code', models.CharField(max_length=15, unique=True)),
                ('day_created', models.DateTimeField(auto_now_add=True)),
                ('usage_count', models.PositiveIntegerField(blank=True, default=100, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=5, max_digits=5)),
                ('type_of_discount', models.CharField(choices=[('a', 'percent'), ('b', 'absolute_price'), ('c', 'multi_buy'), ('d', 'price_reduce'), ('e', 'shipping_free')], max_length=1)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('unique_per_user', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': '2. Κουπόνια',
            },
        ),
    ]
