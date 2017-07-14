# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 05:51
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CheckOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('a', 'Αποπληρωμή Τιμολογίου'), ('b', 'Προκαταβολές'), ('c', 'Επιταγές')], default='c', max_length=1)),
                ('title', models.CharField(blank=True, max_length=64, null=True, verbose_name='Σχόλια')),
                ('value', models.DecimalField(decimal_places=2, max_digits=255, verbose_name='Ποσό')),
                ('date_expire', models.DateField(verbose_name='Ημερομηνία Λήξης')),
                ('day_added', models.DateField(auto_now=True)),
                ('status', models.CharField(choices=[('a', 'Σε εξέλιξη'), ('b', 'Εισπράκτηκε'), ('c', 'Ακυρώθηκε')], default='a', max_length=1, verbose_name='Κατάσταση')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_created', models.DateTimeField(auto_created=True, default=datetime.datetime(2017, 6, 28, 8, 51, 55, 314883))),
                ('code', models.CharField(max_length=40, unique=True, verbose_name='Αριθμός Παραστατικού')),
                ('status', models.CharField(choices=[('a', 'Ολοκληρώθηκε'), ('d', 'Δόσεις'), ('p', 'Σε αναμονή'), ('c', 'Ακυρώθηκε')], default='p', max_length=1, verbose_name='Σε εξέλιξη')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='')),
                ('total_price_no_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Αξία προ έκπτωσης')),
                ('total_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Αξία έκπτωσης')),
                ('total_price_after_discount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Αξία μετά την έκπτωση')),
                ('total_taxes', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Φ.Π.Α')),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Τελική Αξία')),
                ('credit_balance', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Πιστωτικό υπόλοιπο')),
                ('taxes_modifier', models.IntegerField(default=24, verbose_name='ΦΠΑ Τιμολογίου')),
            ],
            options={
                'verbose_name': 'Τιμολόγια   ',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.IntegerField(default=0, verbose_name='Εκπτωση')),
                ('taxes', models.IntegerField(default=24, verbose_name='ΦΠΑ')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Ποσότητα')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Τιμή Μονάδας')),
                ('total_clean_value', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Συνολική Αξία χωρίς Φόρους')),
                ('total_value_with_taxes', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Συνολική Αξία με φόρους')),
                ('day_added', models.DateField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Συστατικά Τιμολογίου   ',
                'ordering': ['product'],
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Υπόλοιπο')),
                ('content', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('for_site', models.BooleanField(default=True)),
            ],
            managers=[
                ('my_query', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethodGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='PayOrders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('a', 'Αποπληρωμή Τιμολογίου'), ('b', 'Προκαταβολές'), ('c', 'Επιταγές')], default='a', max_length=1)),
                ('date', models.DateField(verbose_name='Ημερομηνία')),
                ('value_portion', models.CharField(choices=[('a', 'Εξόφληση συνολικής αξιας'), ('b', 'Δόσεις')], default='b', max_length=1)),
                ('way_of_pay', models.CharField(choices=[('a', 'Μετρητά'), ('b', 'Πιστωτική'), ('c', 'Μέσω Τραπέζης')], default='a', max_length=1, verbose_name='Τρόπος Εξόφλησης')),
                ('receipt', models.CharField(default='---', max_length=64, verbose_name='Απόδειξη')),
                ('value', models.DecimalField(decimal_places=3, default=0, max_digits=10, verbose_name='Ποσό')),
                ('day_added', models.DateField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Εντολές Πληρωμής    ',
            },
        ),
        migrations.CreateModel(
            name='PreOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('a', 'Active'), ('b', 'Used')], default='a', max_length=1)),
                ('day_added', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreOrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=5)),
                ('day_added', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreOrderNewItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('qty', models.DecimalField(decimal_places=2, max_digits=6)),
                ('price_buy', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Τιμή Αγοράς')),
                ('discount_buy', models.IntegerField(default=0, verbose_name='Εκπτωση Τιμολογίου')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Τιμή Λιανικής')),
                ('sku', models.CharField(blank=True, max_length=50, null=True)),
                ('day_added', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreOrderStatement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('day_added', models.DateField(auto_now=True)),
                ('day_expire', models.DateField(auto_now=True)),
                ('send_status', models.BooleanField(default=False)),
                ('is_sended', models.CharField(choices=[('a', 'Ενεργό'), set(['b', 'Στάλθηκε.'])], default='a', max_length=1)),
                ('print_status', models.BooleanField(default=False)),
                ('is_printed', models.CharField(choices=[('a', 'Ενεργό'), set(['b', 'Εκτυπώθηκε.'])], default='a', max_length=1)),
                ('consume_to_order', models.BooleanField(default=False, verbose_name='Μετατροπή σε Τιμολόγιο.')),
            ],
        ),
        migrations.CreateModel(
            name='PreOrderStatementItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=5)),
                ('day_added', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreOrderStatementNewItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('qty', models.DecimalField(decimal_places=2, max_digits=6)),
                ('price_buy', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Τιμή Αγοράς')),
                ('discount_buy', models.IntegerField(default=0, verbose_name='Εκπτωση Τιμολογίου')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Τιμή Λιανικής')),
                ('sku', models.CharField(blank=True, max_length=50, null=True)),
                ('day_added', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=5)),
            ],
            options={
                'verbose_name': 'Μονάδα Μέτρησης  ',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='VendorDepositOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('a', 'Αποπληρωμή Τιμολογίου'), ('b', 'Προκαταβολές'), ('c', 'Επιταγές')], default='b', max_length=1)),
                ('title', models.CharField(blank=True, max_length=64)),
                ('value', models.DecimalField(decimal_places=3, max_digits=10)),
                ('day_added', models.DateField(auto_now=True)),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod')),
            ],
        ),
        migrations.CreateModel(
            name='VendorDepositOrderPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_de', models.CharField(blank=True, max_length=64, verbose_name='Σχόλια')),
                ('value', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Ποσό πληρωμής')),
                ('day_added', models.DateField(verbose_name='Ημερομηνία Πληρωμής')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Order')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής')),
            ],
        ),
    ]