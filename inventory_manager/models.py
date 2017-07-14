from django.db import models
from products.models import *
from decimal import Decimal
# Create your models here.


PAYMENT_TYPE =(('a','Αποπληρωμή Τιμολογίου'),
               ('b','Προκαταβολές'),
               ('c','Επιταγές'),
               )

FPA_CHOICES =(("a",'13'), ("b","23"), ("c","24"), ("d","0"))

def check_taxes(taxes_choice):
    if taxes_choice == 'a':
        return 13
    if taxes_choice == 'b':
        return 23
    if taxes_choice == 'c':
        return 24
    if taxes_choice == 'd':
        return 0

class PaymentMethodGroup(models.Model):
    # grouping of the payment methods , like Bank etc
    title = models.CharField(max_length=64,unique=True)
    balance = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    def __str__(self):
        return self.title

class PaymentMethodManager(models.Manager):
    def active_and_site(self):
        return super(PaymentMethodManager, self).filter(active=True,for_site= True)

class PaymentMethod(models.Model):
    # create a unique Payment method like Cash, Paypal, a specific bank etc and
    # if you want you can group it with the payment_group
    title = models.CharField(max_length=64,unique=True)
    payment_group = models.ForeignKey(PaymentMethodGroup, null=True, blank=True)
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Υπόλοιπο')
    content = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    for_site = models.BooleanField(default=True)
    my_query = PaymentMethodManager()
    objects = models.Manager()
    def __str__(self):
        return self.title

class VendorDepositOrder(models.Model):
    payment_type = models.CharField(default='b',max_length=1, choices=PAYMENT_TYPE)
    title = models.CharField(max_length=64,blank=True)
    payment_method = models.ForeignKey(PaymentMethod)
    vendor = models.ForeignKey(Supply)
    value = models.DecimalField(decimal_places=3,max_digits=10)
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    CHOICES = (('a','Ολοκληρώθηκε'), ('d','Δόσεις'), ('p',"Σε αναμονή"), ("c","Ακυρώθηκε"))
    code = models.CharField(max_length=40, verbose_name="Αριθμός Παραστατικού", unique=True)
    vendor = models.ForeignKey(Supply, verbose_name="Προμηθευτής")
    day_created = models.DateTimeField(auto_created=True, default=datetime.datetime.now())
    status =models.CharField(max_length=1, choices=CHOICES, verbose_name="Σε εξέλιξη", default='p')
    notes = models.TextField(null=True, blank=True, verbose_name="")
    payment_method = models.ForeignKey(PaymentMethod, null=True, verbose_name='Τρόπος Πληρωμής')
    total_price_no_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Αξία προ έκπτωσης")
    total_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Αξία έκπτωσης")
    total_price_after_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Αξία μετά την έκπτωση")
    total_taxes = models.DecimalField(default=0,max_digits=15, decimal_places=2, verbose_name="Φ.Π.Α")
    total_price = models.DecimalField(default=0,max_digits=15, decimal_places=2, verbose_name="Τελική Αξία")
    credit_balance = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Πιστωτικό υπόλοιπο")
    taxes_modifier = models.IntegerField(default=24, verbose_name='ΦΠΑ Τιμολογίου')
    class Meta:
        verbose_name = "Τιμολόγια   "
    def __str__(self):
        return  self.code
    def absolute_url_order(self):
        return reverse('order_edit_main', kwargs={'dk':self.id})
    def ipoloipo_xreostiko(self):
        return self.total_price - self.credit_balance
    def template_tag_total_price(self):
        return '%s %s'%('{0:.2f'.format(round(self.total_price), 2), CURRENCY)
    def dept_remaining(self):
        return self.total_price - self.credit_balance
    def items_count(self):
        all_items = self.orderitem_set.all()
        count = 0
        for item in all_items:
            count += item.qty
        return count


class Unit(models.Model):
    # Τεμάχ,Κιλά, Κιβώτ
    name = models.CharField(max_length=5)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
        verbose_name = "Μονάδα Μέτρησης  "


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product, verbose_name='Προϊόν')
    unit = models.ForeignKey(Unit, verbose_name='Μονάδα Μέτρησης')
    discount = models.IntegerField(default=0, verbose_name='Εκπτωση')
    taxes = models.IntegerField(default=24, verbose_name='ΦΠΑ')
    qty = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Ποσότητα')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Τιμή Μονάδας')
    size = models.ForeignKey(SizeAttribute, verbose_name='Size', null=True, blank=True)
    total_clean_value = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name='Συνολική Αξία χωρίς Φόρους')
    total_value_with_taxes = models.DecimalField(default=0, max_digits=14, decimal_places=2, verbose_name='Συνολική Αξία με φόρους')
    day_added = models.DateField(auto_now=True)
    class Meta:
        ordering = ['product']
        verbose_name = "Συστατικά Τιμολογίου   "
    def __str__(self):
        return self.product.title
    def identity(self):
        return 'buy'
    @property
    def day_created(self):
        return self.order.day_created
    def price_before_discount(self):
        pass
    def price_after_discount(self):
        pr = (self.price - (self.price*self.discount)/100)*self.qty
        return Decimal('%s'%("{0:.2f}".format(round(pr, 2))))
    def price_after_taxes(self):
        price = Decimal(self.price)
        qty = Decimal(self.qty)
        taxes = self.taxes
        taxes =Decimal(taxes)
        discount = self.discount
        discount = (price*discount)/100
        return Decimal(((price - discount)*(100+taxes))/100)
    def total_price_after_discount(self):
        pr = (self.price - (self.price*self.discount)/100)*self.qty
        return pr
    def total_value(self):
        return Decimal(self.qty * self.price_after_taxes())
    def total_taxes(self):
        return Decimal((self.qty *self.price_after_taxes()) - self.total_price_after_discount())
    def update_main_product(self):
        #update_product
        self.product.qty += self.qty
        self.product.price_buy = self.price
        self.product.order_discount = self.discount
        self.product.save()
        #update_order, vendor, and order item
        total_price = self.price * self.qty
        disc = (total_price * self.discount) / 100
        clean_value = total_price - disc
        taxes = (clean_value * (self.taxes)) / 100
        final_value = clean_value + taxes
        order = self.order
        vendor = order.vendor
        order.total_price_no_discount += total_price
        order.total_discount += disc
        order.total_price_after_discount += clean_value
        order.total_taxes += taxes
        order.total_price += final_value
        vendor.balance += final_value
        self.total_clean_value = clean_value
        self.total_value_with_taxes = final_value
        self.save()
        order.save()
        vendor.save()
    def update_size(self):
        self.size.qty += self.qty
        self.size.save()
    def delete_order_item(self):
        #update_product
        self.product.qty -= self.qty
        self.product.save()
        #update_order, vendor, and order item
        total_price = self.price * self.qty
        disc = (total_price * self.discount) / 100
        clean_value = total_price - disc
        taxes = (clean_value * self.taxes) / 100
        final_value = clean_value + taxes
        order = self.order
        vendor = order.vendor
        order.total_price_no_discount -= total_price
        order.total_discount -= disc
        order.total_price_after_discount -= clean_value
        order.total_taxes -= taxes
        order.total_price -= final_value
        vendor.balance -= final_value
        self.total_clean_value = clean_value
        self.total_value_with_taxes = final_value
        self.save()
        order.save()
        vendor.save()
        if self.size:
            self.size.qty -= self.qty
            self.size.save()

    def update_order_item_from_order(self, old_item):
        old_qty = old_item.qty
        print(old_qty)
        old_price = old_item.price
        old_taxes = old_item.taxes
        old_discount = old_item.discount

        self.product.qty += self.qty - old_qty
        self.product.price_buy = self.price
        self.product.order_discount = self.discount
        self.product.save()

        #update_order, vendor, and order item
        total_price = self.price * self.qty
        old_total_price = old_price * old_qty
        disc = (total_price * self.discount) / 100
        old_disc = (old_total_price*old_discount)/100
        clean_value = total_price - disc
        old_clean_value = old_total_price - old_disc
        taxes = (clean_value * (self.taxes)) / 100
        old_tax = (old_clean_value*old_taxes)/100
        final_value = clean_value + taxes
        old_final_value = old_clean_value + old_taxes
        order = self.order
        vendor = order.vendor
        order.total_price_no_discount += total_price - old_total_price
        order.total_discount += disc - old_disc
        order.total_price_after_discount += clean_value - old_clean_value
        order.total_taxes += taxes - old_tax
        order.total_price += final_value - old_final_value
        vendor.balance += final_value - old_final_value
        self.total_clean_value = clean_value
        self.total_value_with_taxes = final_value
        self.save()
        order.save()
        vendor.save()
        if self.size:
            self.size.qty += self.qty - old_qty
            self.save()



    def pre_order_add_to_product(self, product, qty):
        price = self.price
        qty = qty
        discount = self.discount
        my_product = product
        my_product.qty = discount
        my_product.price_buy = price
        my_product.reserve += qty
        my_product.save()

    def pre_order_add_to_color_product(self, product, discount, price, qty):
        #main product
        my_product = product.product
        my_product.qty = discount
        my_product.price_buy = price
        my_product.reserve += qty
        my_product.save()


        my_product_color = product
        my_product_color.order_discount = discount
        my_product_color.price_buy = price
        my_product_color.qty += qty
        my_product_color.save()

    def pre_order_add_to_order(self, qty, order,):

        price = self.price
        qty = qty
        discount = self.discount
        taxes = self.taxes
        taxes=check_taxes(self.taxes)
        fpa = int(taxes)

        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes

        my_order = order
        my_vendor = my_order.vendor

        my_order.total_price_no_discount += total_price
        my_order.total_discount += disc
        my_order.total_price_after_discount += net_income
        my_order.total_taxes += taxes
        my_order.total_price += final_value
        my_vendor.balance += final_value
        my_order.save()
        my_vendor.save()


class PayOrders(models.Model):
    payment_type = models.CharField(default='a', max_length=1, choices=PAYMENT_TYPE)
    CHOICES = (('a','Μετρητά'),('b','Πιστωτική'),('c','Μέσω Τραπέζης'))
    CHOICES2 = (('a','Εξόφληση συνολικής αξιας'),('b','Δόσεις'))
    date = models.DateField(verbose_name='Ημερομηνία')
    title = models.ForeignKey(Order, verbose_name='Αριθμός Παραστατικου')
    payment_method = models.ForeignKey(PaymentMethod, null=True, verbose_name='Τρόπος Πληρωμής')
    #this get removed on new version
    value_portion = models.CharField(default='b', max_length=1, choices=CHOICES2)
    way_of_pay = models.CharField(max_length=1, choices=CHOICES, default='a', verbose_name='Τρόπος Εξόφλησης')
    receipt = models.CharField(max_length=64, default='---', verbose_name='Απόδειξη')
    value = models.DecimalField(default=0, max_digits=10, decimal_places=3, verbose_name='Ποσό')
    day_added = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "Εντολές Πληρωμής    "

    def __str__(self):
        return self.title.code

    def delete_pay(self):
        self.title.credit_balance -= self.value
        self.title.status = 'd'
        self.title.save()
        self.title.vendor.balance += self.value
        self.title.vendor.save()
        
    def delete_pay_order(self, dk=None):
        pay_order = PayOrders.objects.get(id=dk) #this line is useless i gonna delete it when make sure program will not crush
        self.title.credit_balance -= self.value
        self.title.status = 'd'
        self.title.save()
        self.title.vendor.balance += self.value
        self.title.vendor.save()

    def payment_type_vendor_page(self):
        return 'payment_order'


class VendorDepositOrderPay(models.Model):
    # save the payments from deposit option
    title_de = models.CharField(max_length=64, blank=True, verbose_name='Σχόλια')
    payment_method = models.ForeignKey(PaymentMethod, verbose_name='Τρόπος Πληρωμής')
    order = models.ForeignKey(Order)
    value = models.DecimalField(decimal_places=3,max_digits=10, verbose_name='Ποσό πληρωμής')
    day_added = models.DateField(verbose_name='Ημερομηνία Πληρωμής')

    def __str__(self):
        return self.title_de

    def payment_type_vendor_page(self):
        return 'deposit_order'

    def delete_deposit(self):
        self.order.vendor.remaining_deposit += self.value
        self.order.vendor.save()
        self.order.credit_balance -= self.value
        self.order.status = 'd'
        self.order.save()

class CheckOrder(models.Model):
    payment_type = models.CharField(default='c',max_length=1, choices=PAYMENT_TYPE)
    CHOICES= (('a','Σε εξέλιξη'), ('b','Εισπράκτηκε'), ('c','Ακυρώθηκε'),)
    title = models.CharField(max_length=64,blank=True, null=True, verbose_name='Σχόλια')
    order_related = models.ForeignKey(Order, blank=True, null=True)
    value = models.DecimalField(decimal_places=2, max_digits=255, verbose_name="Ποσό")
    debtor  =models.ForeignKey(Supply, verbose_name='Πιστωτής')
    place = models.ForeignKey(PaymentMethod, verbose_name='Τόπος- Τράπεζα')
    date_expire = models.DateField(verbose_name='Ημερομηνία Λήξης')
    day_added = models.DateField(auto_now=True)
    status = models.CharField(max_length=1, choices=CHOICES, default='a', verbose_name='Κατάσταση')

    def __str__(self):
        return self.title

class PreOrder(models.Model):
    STATUS= (('a','Active'), ('b','Used'))
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1, choices=STATUS, default='a')
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

class PreOrderItem(models.Model):
    title = models.ForeignKey(Product)
    order = models.ForeignKey(PreOrder)
    qty = models.DecimalField(decimal_places=2, max_digits=5)
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title.title

class PreOrderNewItem(models.Model):
    title = models.CharField(max_length=120)
    vendor = models.ForeignKey(Supply)
    qty = models.DecimalField(max_digits=6,decimal_places=2)
    price_buy = models.DecimalField(default=0,max_digits=6,decimal_places=2, verbose_name='Τιμή Αγοράς')
    discount_buy = models.IntegerField(default=0, verbose_name='Εκπτωση Τιμολογίου')
    price = models.DecimalField(default=0,max_digits=6,decimal_places=2, verbose_name='Τιμή Λιανικής')
    sku = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, null=True)
    brand = models.ForeignKey(Brands, blank=True,null=True)
    color = models.ForeignKey(Color, blank=True, null=True)
    size = models.ForeignKey(Size, blank=True, null=True)

    day_added = models.DateField(auto_now=True)
    order = models.ForeignKey(PreOrder)

    def __str__(self):
        return self.title

class PreOrderStatement(models.Model):
    STATUS=(('a','Ενεργό'),{'b','Στάλθηκε.'})
    STATUS_P=(('a','Ενεργό'),{'b','Εκτυπώθηκε.'})
    title = models.CharField(max_length=100)
    day_added = models.DateField(auto_now=True)
    day_expire = models.DateField(auto_now=True)
    vendor = models.ForeignKey(Supply)
    send_status = models.BooleanField(default=False)
    is_sended  = models.CharField(max_length=1, choices=STATUS, default='a')
    print_status = models.BooleanField(default=False)
    is_printed = models.CharField(default='a', max_length=1, choices=STATUS_P)
    consume_to_order = models.BooleanField(default=False, verbose_name='Μετατροπή σε Τιμολόγιο.')

    def __str__(self):
        return self.title

class PreOrderStatementItem(models.Model):
    title = models.ForeignKey(Product)
    order = models.ForeignKey(PreOrderStatement)
    qty = models.DecimalField(decimal_places=2, max_digits=5)
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title.title

class PreOrderStatementNewItem(models.Model):
    title = models.CharField(max_length=120)
    vendor = models.ForeignKey(Supply)
    qty = models.DecimalField(max_digits=6,decimal_places=2)
    price_buy = models.DecimalField(default=0,max_digits=6,decimal_places=2,verbose_name='Τιμή Αγοράς')
    discount_buy = models.IntegerField(default=0, verbose_name='Εκπτωση Τιμολογίου')
    price = models.DecimalField(default=0,max_digits=6,decimal_places=2, verbose_name='Τιμή Λιανικής')
    sku = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, null=True)
    brand = models.ForeignKey(Brands, blank=True,null=True)
    color = models.ForeignKey(Color, blank=True, null=True)
    size = models.ForeignKey(Size, blank=True, null=True)

    day_added = models.DateField(auto_now=True)
    order = models.ForeignKey(PreOrderStatement)

    def __str__(self):
        return self.title
