from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from products.models import TaxesCity
# Create your models here.

CURRENCY = '€'

class CostumerAccount(models.Model):
    user = models.OneToOneField(User, blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name='Ονομα')
    last_name = models.CharField(max_length=100,  verbose_name='Επίθετο')
    #shipping_information
    shipping_address_1 = models.CharField(max_length=100,blank=True, null=True, verbose_name='Διεύθυνση Αποστολής')
    shipping_city = models.CharField(max_length=50, blank=True, null=True, verbose_name='Πόλη')
    shipping_zip_code= models.IntegerField(blank=True, null=True, verbose_name='Ταχυδρομικός Κώδικας')
    #billing information
    billing_name = models.CharField(max_length=100, blank=True, null=True)
    billing_address = models.CharField(max_length=100, blank=True, null=True)
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_zip_code = models.IntegerField(blank= True, null=True, )
    #personal stuff
    phone = models.CharField(max_length=10, blank=True, verbose_name="Τηλέφωνο")
    phone1 = models.CharField(max_length=10, blank=True, verbose_name="Τηλέφωνο")
    cellphone = models.CharField(max_length=10, blank=True, verbose_name='Κινητό')
    fax = models.CharField(max_length=10, blank=True, verbose_name="Fax")
    #if costumer is not Retail
    is_retail = models.BooleanField(default=True)
    is_eshop = models.BooleanField(default=True)
    afm = models.CharField(max_length=9, blank=True, verbose_name="ΑΦΜ")
    DOY = models.ForeignKey(TaxesCity, verbose_name='Εφορία', blank=True, null=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Υπόλοιπο')
    paid_value = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Πιστωτικό Υπόλοιπο')
    total_order_value = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Χρεωστικό Υπόλοιπο')
    def full_name(self):
        return '%s  %s'%(self.first_name,self.last_name)

    def __str__(self):
        return self.full_name()

    def template_tag_balance(self):
        return '%s %s'%('{0:2f}'.format(round(self.balance, 2)),CURRENCY)

    def template_tag_paid_value(self):
        return '%s %s'%('{0:2f}'.format(round(self.paid_value, 2)),CURRENCY)

    def template_tag_diff(self):
        diff = self.balance - self.paid_value
        return '%s %s'%('{0:2f}'.format(round(diff, 2)),CURRENCY)
    @property
    def get_content_type(self):
        instance  = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type
    def remaining_value(self):
        return self.balance - self.paid_value
