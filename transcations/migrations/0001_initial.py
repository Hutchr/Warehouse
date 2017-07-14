# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 05:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryPersonPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, unique=True)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('remaining_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='CreatePersonSalaryCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='Περιγραφή')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Αξία')),
                ('day_added', models.DateField(auto_now=True)),
                ('day_expire', models.DateField(default=django.utils.timezone.now, verbose_name='Πληρωμή μέχρι .....')),
                ('status', models.CharField(choices=[('a', 'Ενεργός'), ('b', 'Μη Ενεργός')], default='a', max_length=1)),
                ('paid_value', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.CategoryPersonPay', verbose_name='Είδος Πληρωμής')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής')),
            ],
            options={
                'verbose_name': 'Εντολές Πληρωμής Υπαλλήλων. ',
            },
        ),
        migrations.CreateModel(
            name='Fixed_costs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True)),
                ('total_pay', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('total_dept', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Χρεωστικό Υπόλοιπο')),
            ],
            options={
                'verbose_name': 'Κεντρική Κατηγορία Εξόδων   ',
            },
        ),
        migrations.CreateModel(
            name='Fixed_Costs_item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Ονομασία Κατηγορίας')),
                ('total_pay', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('total_dept', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Χρεωστικό Υπόλοιπο')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Fixed_costs')),
            ],
            options={
                'verbose_name': 'Λογαριασμοί και Πάγια έξοδα',
            },
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Απασχόληση')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Σημειώσεις')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Συνολικά Έξοδα')),
                ('remaining_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Fixed_costs')),
            ],
            options={
                'verbose_name': 'Απασχόληση   ',
            },
        ),
        migrations.CreateModel(
            name='Order_Fixed_Cost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='Αρ.Παραστατικού/Σχολιασμός')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Ημερομηνία Λήξης')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Ποσό Πληρωμής')),
                ('credit_balance', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('active', models.CharField(choices=[('a', 'Απλήρωτη'), ('b', 'Πληρώθηκε')], default='a', max_length=1)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Fixed_Costs_item', verbose_name='Λογαριασμός')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής')),
            ],
            options={
                'verbose_name': 'Εντολές Πληρωμών',
            },
        ),
        migrations.CreateModel(
            name='Pagia_Exoda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Σημειώσεις')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Συνολικά Έξοδα')),
                ('remaining_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Fixed_costs')),
            ],
        ),
        migrations.CreateModel(
            name='Pagia_Exoda_Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Αρ.Παραστατικού')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Ημερομηνία Λήξης')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Αξία')),
                ('credit_balance', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Υπόλοιπο')),
                ('active', models.CharField(choices=[('a', 'Απλήρωτη'), ('b', 'Πληρώθηκε')], default='a', max_length=1)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Pagia_Exoda', verbose_name='Λογαριασμός')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής')),
            ],
        ),
        migrations.CreateModel(
            name='Pagia_Exoda_Pay_Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Περιγραφή')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Αξία')),
                ('day_added', models.DateField(auto_now=True)),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής')),
            ],
            options={
                'verbose_name': 'Αποδείξη Πληρωμής Πάγια',
            },
        ),
        migrations.CreateModel(
            name='PayOrderFixedCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='Αρ.Παραστατικού')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Ημερομηνία Πληρωμής')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Αξία')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής')),
            ],
            options={
                'verbose_name': 'Αποδείξη Πληρωμής',
            },
        ),
        migrations.CreateModel(
            name='PayPersonSalaryCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='Περιγραφή')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Αξία')),
                ('day_added', models.DateField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.CategoryPersonPay', verbose_name='Είδος Πληρωμής')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής')),
            ],
            options={
                'verbose_name': 'Αποδείξη Πληρωμής Υπαλλήλων',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Ονοματεπώνυμο')),
                ('phone', models.CharField(blank=True, max_length=10, verbose_name='Τηλέφωνο')),
                ('phone1', models.CharField(blank=True, max_length=10, verbose_name='Κινητό')),
                ('date_joined', models.DateField(default=django.utils.timezone.now, verbose_name='Ημερομηνία Πρόσληψης')),
                ('total_amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Συνολική Πληρωμή')),
                ('status', models.CharField(choices=[('a', 'Ενεργός'), ('b', 'Μη Ενεργός')], default='a', max_length=1)),
                ('hour_salary_sum', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Υπόλοιπο Υπερωρίων')),
                ('salary_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Πιστωτικό Υπόλοιπο')),
                ('occupation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Occupation', verbose_name='Απασχόληση')),
            ],
            options={
                'verbose_name': 'Υπάλληλος   ',
            },
        ),
        migrations.CreateModel(
            name='PersonHoursCreate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Περιγραφή')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Αξία')),
                ('day_added', models.DateField(auto_now=True)),
                ('day_expire', models.DateField(default=django.utils.timezone.now, verbose_name='Πληρωμή μέχρι .....')),
                ('status', models.CharField(choices=[('a', 'Ενεργός'), ('b', 'Μη Ενεργός')], default='a', max_length=1)),
                ('times_per_month', models.DecimalField(decimal_places=1, default=0, max_digits=4, verbose_name='Υπερωρίες')),
                ('hour_salary', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Ωρομίσθιο')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Person', verbose_name='Υπάλληλος')),
            ],
            options={
                'verbose_name': 'Εντολές Πληρωμών-Not Working',
            },
        ),
        migrations.CreateModel(
            name='PersonHoursPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Περιγραφή')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Αξία')),
                ('day_added', models.DateField(auto_now=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Person', verbose_name='Υπάλληλος')),
            ],
        ),
        migrations.CreateModel(
            name='PersonMastoras',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Εταιρία/Ονοματεπώνυμο')),
                ('phone', models.CharField(blank=True, max_length=10, null=True, verbose_name='Τηλέφωνο')),
                ('phone1', models.CharField(blank=True, max_length=10, null=True, verbose_name='Κινητό')),
                ('occupation', models.CharField(blank=True, max_length=100, null=True, verbose_name='Απασχόληση')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Συνολικά Έξοδα')),
                ('remaining_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Πιστωτικό Υπόλοιπο')),
            ],
        ),
        migrations.AddField(
            model_name='paypersonsalarycost',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Person', verbose_name='Υπάλληλος'),
        ),
        migrations.AddField(
            model_name='pagia_exoda_pay_order',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.PersonMastoras', verbose_name='Εταιρία'),
        ),
        migrations.AddField(
            model_name='pagia_exoda_order',
            name='person',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='transcations.PersonMastoras', verbose_name='Εταιρία'),
        ),
        migrations.AddField(
            model_name='createpersonsalarycost',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcations.Person', verbose_name='Υπάλληλος'),
        ),
    ]