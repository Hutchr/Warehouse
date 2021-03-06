# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 05:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory_manager', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendordepositorder',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Supply'),
        ),
        migrations.AddField(
            model_name='preorderstatementnewitem',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Brands'),
        ),
        migrations.AddField(
            model_name='preorderstatementnewitem',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Category'),
        ),
        migrations.AddField(
            model_name='preorderstatementnewitem',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Color'),
        ),
        migrations.AddField(
            model_name='preorderstatementnewitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PreOrderStatement'),
        ),
        migrations.AddField(
            model_name='preorderstatementnewitem',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Size'),
        ),
        migrations.AddField(
            model_name='preorderstatementnewitem',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Supply'),
        ),
        migrations.AddField(
            model_name='preorderstatementitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PreOrderStatement'),
        ),
        migrations.AddField(
            model_name='preorderstatementitem',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product'),
        ),
        migrations.AddField(
            model_name='preorderstatement',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Supply'),
        ),
        migrations.AddField(
            model_name='preordernewitem',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Brands'),
        ),
        migrations.AddField(
            model_name='preordernewitem',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Category'),
        ),
        migrations.AddField(
            model_name='preordernewitem',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Color'),
        ),
        migrations.AddField(
            model_name='preordernewitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PreOrder'),
        ),
        migrations.AddField(
            model_name='preordernewitem',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Size'),
        ),
        migrations.AddField(
            model_name='preordernewitem',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Supply'),
        ),
        migrations.AddField(
            model_name='preorderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PreOrder'),
        ),
        migrations.AddField(
            model_name='preorderitem',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product'),
        ),
        migrations.AddField(
            model_name='payorders',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής'),
        ),
        migrations.AddField(
            model_name='payorders',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Order', verbose_name='Αριθμός Παραστατικου'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='payment_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethodGroup'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Order'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product', verbose_name='Προϊόν'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.SizeAttribute', verbose_name='Size'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Unit', verbose_name='Μονάδα Μέτρησης'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τρόπος Πληρωμής'),
        ),
        migrations.AddField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Supply', verbose_name='Προμηθευτής'),
        ),
        migrations.AddField(
            model_name='checkorder',
            name='debtor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Supply', verbose_name='Πιστωτής'),
        ),
        migrations.AddField(
            model_name='checkorder',
            name='order_related',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.Order'),
        ),
        migrations.AddField(
            model_name='checkorder',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory_manager.PaymentMethod', verbose_name='Τόπος- Τράπεζα'),
        ),
    ]
