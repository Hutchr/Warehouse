from django.db import models
from products.models import *
from inventory_manager.models import *
from django.utils import timezone
from account.models import CostumerAccount
from django.contrib import messages
from django.contrib.auth.models import User
import datetime
# Create your models here.

ORDER_TYPES = [('r','retail'), ('e','eshop'), ('b','return'), ('d','destroy')]

#-------------------------Lianiki, epistrofes--------------------------------------------------------------------------------------

class Order_status(models.Model):
    title = models.CharField(max_length=120,unique=True)
    sort_id = models.IntegerField(default=1)

    class Meta:
        ordering = ['sort_id']
    def __str__(self):
        return self.title

class ShippingManager(models.Manager):

    def active_and_site(self):
        return super(ShippingManager, self).filter(active ='a',for_site=True)

class Shipping(models.Model):
    CHOICES = (('a','Active'),('b','Inactive'))
    title = models.CharField(max_length=100,unique=True)
    content = models.CharField(max_length=300,default='Input here')
    active = models.CharField(max_length=1, choices=CHOICES)
    for_site = models.BooleanField(default=True, verbose_name='Ενεργό για το Site')
    objects= models.Manager()
    my_query = ShippingManager()

    def __str__(self):
        return self.title

    def id_str(self):
        return str(self.id)

class RetailOrderManager(models.Manager):
    def sellings_done(self):
        return super(RetailOrderManager, self).filter(status__id=7).exclude(order_type ='b')
    def sellings_not_done(self):
        return super(RetailOrderManager, self).exclude(status__id__in=[7,8], order_type='b')
    def eshop_orders(self):
        return super(RetailOrderManager, self).filter(order_type='e')
    def eshop_new_orders(self):
        return super(RetailOrderManager, self).filter(order_type='e', status_id=1).order_by('-id')
    def eshop_done_orders(self, date_start, date_end):
        return super(RetailOrderManager, self).filter(order_type__in=['e','r'], status__id=7, day_created__range=[date_start, date_end])
    def eshop_orders_on_progress(self):
        return super(RetailOrderManager, self).filter(order_type='e', status__id__in=[2,3,4,5])
    def eshop_orders_in_warehouse(self):
        return super(RetailOrderManager, self).filter(order_type='e', status__id__in=[1,2,3,4,5])

class RetailOrderItemManager(models.Manager):
    def selling_order_items(self, date_start, date_end):
        return super(RetailOrderItemManager, self).filter(order__order_type__in=['e', 's'],
                                                          order__status__id=7,
                                                          order__day_created__range=[date_start, date_end])
    def return_order_items(self, date_start, date_end):
        return super(RetailOrderItemManager ,self).filter(order__order_type ='b',
                                                          order__day_created__range =[date_start, date_end])


class RetailOrder(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    order_type = models.CharField(max_length=1, choices=ORDER_TYPES)
    status = models.ForeignKey(Order_status, null=True, blank=True)
    day_created = models.DateTimeField(default=datetime.datetime.now())
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Έκπτωση',)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Αξία Παραγγελίας')
    total_cost  = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Συνολικό Κόστος Παραγγελίας')
    paid_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Αποπληρωμένο Πόσο')
    costumer_account = models.ForeignKey(CostumerAccount, null=True)
    seller_account =  models.ForeignKey(User, blank=True, null=True)
    payment_method = models.ForeignKey(PaymentMethod, null=True)
    taxes = models.IntegerField(default=24)
    shipping = models.ForeignKey(Shipping, null=True, blank=True)
    shipping_cost = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    day_sent = models.DateTimeField(blank=True, null=True)
    #eshop info only
    first_name= models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.IntegerField(null=True, blank=True)
    cellphone = models.IntegerField(null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    costumer_submit = models.BooleanField(default=True)
    eshop_order_id =models.CharField(max_length=10, blank=True, null=True)
    eshop_session_id = models.CharField(max_length=50, blank=True, null=True)
    my_query = RetailOrderManager()
    objects = models.Manager()
    def __str__(self):
        if self.title:
            return self.title
        return 'order'
    def order_items(self):
        return RetailOrderItem.objects.filter(order=self)
    def tag_total_value(self):
        return '%s %s' %(self.value, CURRENCY )
    def tag_paid_value(self):
        return '%s %s'%(self.paid_value, CURRENCY)
    def remaining_value(self):
        return self.value - self.paid_value
    def order_taxes(self):
        return Decimal((self.taxes*self.paid_value)/100)
    def order_clean_value(self):
        return Decimal(self.paid_value - self.order_taxes())
    def template_tag_value(self):
        return ("{0:.2f}".format(round(self.value,2))) + ' %s'%(CURRENCY)
    def template_tag_paid_value(self):
        return ("{0:.2f}".format(round(self.paid_value,2))) + ' %s'%(CURRENCY)
    def template_tag_taxes(self):
        return '%s %s' %('{0:.2f}'.format(round(self.order_taxes()), 2),CURRENCY)
    def template_tag_full_name(self):
        return '%s %s'%(self.first_name, self.last_name)
    def template_tag_discount(self):
        return '%s %s' %('{0:.2f}'.format((round(self.discount)),2), CURRENCY)
    def template_tag_clean_incomes(self):
        return '%s %s'%(self.order_clean_value() - self.total_cost, CURRENCY)
    def template_tag_order_items_value(self):
        return '%s %s' %((self.value - self.shipping_cost),CURRENCY)


class RetailOrderItem(models.Model):
    title = models.ForeignKey(Product)
    order = models.ForeignKey(RetailOrder)
    cost =  models.DecimalField(max_digits=6, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Τιμή Μονάδας')
    qty = models.DecimalField(max_digits=6, decimal_places=2, default=1, verbose_name='Ποσότητα')
    day_added = models.DateField(auto_now=True)
    #warehouse_management
    is_find = models.BooleanField(default=False)
    #if needed
    size = models.ForeignKey(SizeAttribute, blank=True ,null=True)
    is_return = models.BooleanField(default=False)
    my_query = RetailOrderItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.title.title

    def tag_type_of_order(self):
        if self.order.order_type == 'b':
            return 'Επιστροφή'
        return 'Πώληση'

    def identity(self):
        if self.order.order_type == 'b':
            return 'return'
        return 'sell'

    @property
    def day_created(self):
        return self.order.day_created

    # STRINGS FOR THE TEMPLATE TAG

    def template_tag_color(self):
        if self.color:
            return self.color.title
        if self.title.color_a:
            return self.title.color_a
        return  ''

    def template_tag_size(self):
        if self.size:
            return self.size.title
        if self.title.size_a:
            return self.title.size_a
        return  ''

    def template_tag_price(self):
        return ("{0:.2f}".format(round(self.price,2))) + ' %s'%(CURRENCY)

    def template_tag_total_price(self):
        return "{0:.2f}".format(round(self.price*self.qty,2)) + ' %s'%(CURRENCY)

    def price_for_vendor_page(self):
        #returns silimar def for price in vendor_id page
        return self.price

    def absolute_url_vendor_page(self):
        return reverse('retail_order_section',kwargs={'dk':self.order.id})

    def total_price_number(self):
        return Decimal(self.qty*self.price)

    def total_cost(self):
        return Decimal(self.qty*self.cost)

    def total_taxes(self):
        try:
            return self.total_price_number()*Decimal(self.order.taxes/100)
        except:
            return 0

    def total_price(self):
       return str(self.qty*self.price)

    def delete_from_order_with_color(self, color_attritube, size_attritube):
        #this used with the next one, its additional code
        # to delete the extra models. If the product have color is checked always
        #from the view
        color_attritube.qty +=1
        color_attritube.save()
        size_attritube.qty += 1
        size_attritube.save()

    def delete_from_order_with_only_color(self, color_attritube):
        #this used with the next one, its additional code
        # to delete the extra models. If the product have color is checked always
        #from the view
        color_attritube.qty +=1
        color_attritube.save()

    def add_item_auto(self):
        if self.order.order_type == 'r' or self.order.order_type == 'e':
            if self.order.costumer_account:
                self.order.costumer_account.balance += self.price * self.qty
                self.order.costumer_account.total_order_value += self.price * self.qty
                self.order.costumer_account.save()

            #updates the order
            self.order.value += self.total_price_number()
            self.order.total_cost += self.total_cost()
            self.order.save()
            #updates the warehouse
            if self.title.qty_kilo != 0:
                self.title.qty -= self.qty/self.title.qty_kilo
                self.title.save()
            else:
                self.title.qty -= self.qty
                self.title.save()

        if self.order.order_type == 'b':
            if self.order.costumer_account:
                self.order.costumer_account.balance -= self.price * self.qty
                self.order.costumer_account.total_order_value -= self.price * self.qty
                self.order.costumer_account.save()

            #updates the order
            self.order.value += self.total_price_number()
            self.order.total_cost += self.total_cost()
            self.order.save()
            #updates the warehouse
            if self.title.qty_kilo != 0:
                self.title.qty += self.qty/self.title.qty_kilo
                self.title.save()
            else:
                self.title.qty += self.qty
                self.title.save()
        if self.order.order_type == 'd':
            if self.order.costumer_account:
                self.order.costumer_account.balance -= self.price * self.qty
                self.order.costumer_account.save()

            #updates the order
            self.order.value += self.total_price_number()
            self.order.total_cost += self.total_cost()
            self.order.save()
            #updates the warehouse
            if self.title.qty_kilo != 0:
                self.title.qty += self.qty/self.title.qty_kilo
                self.title.save()
            else:
                self.title.qty += self.qty
                self.title.save()

    def update_order_and_warehouse_with_size(self):
        self.order.total_cost += Decimal(self.cost) * Decimal(self.qty)
        self.order.value += Decimal(self.price) * Decimal(self.qty)
        self.order.save()
        self.title.qty -= Decimal(self.qty)
        self.title.save()
        self.size.qty -= Decimal(self.qty)
        self.size.save()

    def order_type_for_vendor(self):
        return 'sell'

    def delete_from_order(self):
        if self.order.order_type == 'r' or self.order.order_type == 'e':
            self.order.costumer_account.balance -= self.price*self.qty
            self.order.costumer_account.total_order_value -= self.price*self.qty
            self.order.costumer_account.paid_value -= self.price*self.qty
            self.order.costumer_account.save()
            #update order
            price = self.price
            cost =self.cost
            qty = self.qty
            value = price*qty
            cost_value = cost*qty
            self.order.value -= Decimal(value)
            self.order.total_cost -= Decimal(cost_value)
            self.order.save()
            #update warehouse
            product = self.title
            if product.qty_kilo !=0:
                product.qty += qty/product.qty_kilo
            else:
                product.qty += qty
            product.save()

            if self.size:
                self.size.qty += qty
                self.size.save()
        if self.order.order_type == 'b':
            self.order.costumer_account.balance += self.price*self.qty
            self.order.costumer_account.total_order_value += self.price*self.qty
            self.order.costumer_account.paid_value += self.price*self.qty
            self.order.costumer_account.save()
            #update order
            price = self.price
            cost =self.cost
            qty = self.qty
            value = price*qty
            cost_value = cost*qty
            self.order.value -= Decimal(value)
            self.order.total_cost -= Decimal(cost_value)
            self.order.save()
            #update warehouse
            product = self.title
            if product.qty_kilo !=0:
                product.qty -= qty/product.qty_kilo
            else:
                product.qty -= qty
            product.save()

            if self.size:
                self.size.qty -= qty
                self.size.save()

def create_destroy_title():
    last_order = DestroyOrder.objects.all().last()
    if last_order:
        number = int(last_order.id)+1
        return 'ΚΑΤ'+ str(number)
    else:
        return 'ΚΑΤ1'

class DestroyOrder(models.Model):
    title = models.CharField(max_length=15,default=create_destroy_title)
    day_added =models.DateTimeField(auto_now=True)
    total_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    notes = models.CharField(max_length=150, blank=True, null=True)

class DestroyOrderItem(models.Model):
    title = models.ForeignKey(Product)
    order = models.ForeignKey(DestroyOrder)
    cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    qty = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    day_added = models.DateField(auto_now=True)
    size = models.ForeignKey(SizeAttribute, blank=True ,null=True)

    def __str__(self):
        return self.title.title

    def edit_order_item(self):
        pass

    def total_cost(self):
        return self.qty*self.cost

    def delete_order_item(self,order, order_item):
        total_cost =order_item.cost*order_item.qty
        order.total_cost -= total_cost
        product = order_item.title
        product.qty +=order_item.qty
        product.save()
        order.save()

    def delete_order_item_with_color(self):
        self.size.qty += self.qty
        self.size.save()

    def update_warehouse_and_order(self):
        self.order.total_cost += self.qty*self.cost
        self.order.save()
        self.title.qty -= self.qty
        self.title.save()

    def update_warehouse_with_color(self):
        self.size.qty -= self.qty
        self.size.save()

    def order_type_for_vendor(self):
        return 'destroy'


