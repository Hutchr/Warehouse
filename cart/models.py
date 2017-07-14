from django.db import models
from products.models import Product, SizeAttribute

from products.models import CategorySite, Category, Product, Brands
from newsletter.models import NewsLetterUser
from django.contrib.auth.models import User
# Create your models here.

class CartItemManager(models.Manager):
    def current_session_and_active(self, cart_id):
        return super(CartItemManager, self).filter(cart_id=cart_id,is_active= True, is_ordered =False)

class Voucher(models.Model):
    DISCOUNT_TYPE = (('a','percent'), ('b','absolute_price'), ('c', 'multi_buy'), ('d','price_reduce'), ('e', 'shipping_free'))
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    coupon_code = models.CharField(unique=True, max_length=15)
    day_created = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=100, blank=True, null=True)
    price = models.DecimalField(default=5, max_digits=5, decimal_places=2)
    type_of_discount = models.CharField(max_length=1, choices=DISCOUNT_TYPE)
    category_affects = models.ManyToManyField(Category, blank=True)
    products_affects = models.ManyToManyField(Product, blank=True)
    brands_affects = models.ManyToManyField(Brands, blank=True)
    date_start = models.DateField()
    date_end = models.DateField()
    unique_per_user = models.BooleanField(default=False)
    users = models.ManyToManyField(User, blank=True, null=True)
    email = models.ManyToManyField(NewsLetterUser, blank=True, null=True)
    class Meta:
        verbose_name_plural = '2. Κουπόνια'
    def __str__(self):
        return self.title

class CartRules(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    shipping_cost = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    shipping_cost_limit = models.DecimalField(max_digits=5, decimal_places=2, default=35, verbose_name='Όριο Αξίας Μεταφορικών')
    cash_on_delivery_cost = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    cash_on_delivery_limit = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name='Όριο Αξίας Μεταφορικών')
    class Meta:
        verbose_name_plural = '1. Κανόνες Καλαθιού'

class CartOrder(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    vouchers = models.ManyToManyField(Voucher, blank=True)
    is_active = models.BooleanField(default=True)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    qty = models.IntegerField(default=1)
    size = models.ForeignKey(SizeAttribute, null=True, blank=True)
    product = models.ForeignKey(Product)
    is_active = models.BooleanField(default=True)
    is_ordered =models.BooleanField(default=False)
    my_query = CartItemManager()
    objects = models.Manager()
    retated_order = models.ForeignKey(CartOrder, blank=True, null=True)
    def __str__(self):
        return self.cart_id
    class Meta:
        ordering = ['date_added']

    def total(self):
        return self.qty* self.product.price

    def name(self):
        return self.product.title

    def price(self):
        return self.product.site_price

    def augment_quantity(self, quantity):
        self.qty = self.qty + int(quantity)
        self.save()

    def eshop_confirm_order(self):
        self.product.qty -= self.qty
        if self.size:
            self.size.qty -= self.qty
            self.size.save()
        self.product.save()






