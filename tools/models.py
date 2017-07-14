from django.db import models
from products.models import Product
# Create your models here.






class ToolsTableOrder(models.Model):
    #you control here the table
    title = models.CharField(max_length=64,unique=True)
    show_number_of_products = models.IntegerField(default=50, verbose_name='Επέλεξε Πόσα Προιόντα θα εμφανίζονται ')
    width = models.IntegerField(default=120, verbose_name='Μήκος Τραπεζιού')
    height = models.IntegerField(default=600, verbose_name='Υψος Τραπεζιού')
    table_order_by=models.CharField(blank=True, default=None, max_length=100, verbose_name='')

    def __str__(self):
        return self.title


class Discount(models.Model):
    TYPE = (('a', 'Ποσοστό'), ('b','Ποσό'))
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=60)
    date_start = models.DateField()
    date_end = models.DateField()
    type_of_discount = models.CharField(max_length=1, choices=TYPE,)
    value = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    query_set = models.ManyToManyField(Product)

    def __str__(self):
        return self.title

    def period(self):
        return '%s-%s' % (self.date_start, self.date_end)

