# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 05:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart', '0001_initial'),
        ('newsletter', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='brands_affects',
            field=models.ManyToManyField(blank=True, to='products.Brands'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='category_affects',
            field=models.ManyToManyField(blank=True, to='products.Category'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='email',
            field=models.ManyToManyField(blank=True, null=True, to='newsletter.NewsLetterUser'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='products_affects',
            field=models.ManyToManyField(blank=True, to='products.Product'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cartorder',
            name='vouchers',
            field=models.ManyToManyField(blank=True, to='cart.Voucher'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='retated_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cart.CartOrder'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.SizeAttribute'),
        ),
    ]