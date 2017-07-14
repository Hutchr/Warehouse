from django.conf import settings
from django.db import models
import os
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from time import time
import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from smartfields import fields
from smartfields.dependencies import FileDependency
from smartfields.processors import ImageProcessor
# Create your models here.
from decimal import Decimal
CURRENCY = '€'
FPA = 1.24
#MEDIAURL = 'media'
MEDIAURL = 'https://monastiraki.s3.amazonaws.com/media/'
FOCUS = (
    ('a','Active'),
    ('n','Not active')
)
STATUS = (
    ('a','Σε απόθεμα'),
    ('i','Inactive'),
    ('o','Διαθέσιμο με παραγγελία'),
    ('p','Προσωρινά μη διαθέσιμο'),
)

def product_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'product/{0}/{1}'.format(instance.product.title, filename)

def category_site_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'category_site/{0}/{1}'.format(instance.title, filename)

def upload_location(instance, filename):
    return "%s%s" %(instance.id, filename)

def my_awesome_upload_function(instance, filename):
    """ this function has to return the location to upload the file """
    return os.path.join('/media_cdn/%s/' % instance.id, filename)

class ProductManager(models.Manager):
    def active_warehouse(self):
        return super(ProductManager, self).filter(ware_active=True)
    def active_for_site(self):
        return super(ProductManager, self).filter(ware_active=True, status=True)
    def active_with_qty(self):
        return super(ProductManager, self).filter(ware_active=True, status= True, qty__gte=1)
    def active_with_brand(self, brand):
        return super(ProductManager, self).filter(brand__id=brand, ware_active=True, status=True)
    def active_category_site(self,id):
        return super(ProductManager, self).filter(ware_active=True, status=True, category_site=CategorySite.objects.get(id=id))
    def active_get_all_category_site(self,list_of_category):
        return super(ProductManager, self).filter(ware_active=True, status= True, qty__gte=1, category_site__in=list_of_category)
    def active_get_one_category_site(self,category):
        return super(ProductManager, self).filter(ware_active=True, status=True, category_site=category)
    def site_offers(self):
        return super(ProductManager, self).filter(price_discount__gte=0.01, ware_active=True, status=True, qty__gte=1)

class CategorySiteManager(models.Manager):
    def main_page_show(self):
        return super(CategorySiteManager, self).filter(status='a', category__isnull=True)

class CategorySite(models.Model):
    CHOICES = (('a','active'),('b','inactive'))
    title = models.CharField(max_length=120,unique=True)
    image = models.ImageField(blank=True, null=True, upload_to=category_site_directory_path, help_text='610*410')
    content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=CHOICES, default='a')
    sort_order = models.IntegerField(default=1)
    date_added = models.DateField(auto_now=True)
    seo_keyword= models.CharField(max_length=300,blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey('self', blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    my_query = CategorySiteManager()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '3. Κατηγορίες Site'
        unique_together = ('slug', 'category')

    def __str__(self):
        full_path = [self.title]
        k = self.category
        while k is not None:
            full_path.append(k.title)
            k = k.category
        return ' -> '.join(full_path[::-1])

    def absolute_url_site(self):
        pass

    def image_tag(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="400px" height="400px" />'%(MEDIAURL, self.image))
    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="100px" height="100px" />'%(MEDIAURL, self.image))
    image_tag.short_description = 'Είκονα'
    def is_parent(self):
        if self.category:
            return False
        return True
    def is_first_born(self):
        try:
            if self.category.category:
                return False
        except:
            if self.category:
                return True
            return False

    def is_second_child(self):
        try:
            if self.category.category:
                return True
        except:
            return False

class Brands(models.Model):
    title = models.CharField(max_length=120, unique=True, verbose_name='Ονομασία Brand')
    image = models.ImageField(blank=True, upload_to='brands/', verbose_name='Εικόνα')
    order_by = models.IntegerField(default=1,verbose_name='Σειρά Προτεριότητας')
    meta_keywords = models.CharField(max_length=255, blank=True)
    meta_description =models.CharField(max_length=255, blank=True)
    width = models.IntegerField(default=240)
    height = models.IntegerField(default=240)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    is_active= models.BooleanField(default=True, verbose_name='Ενεργοποίηση')

    class Meta:
        verbose_name_plural = '4. Brands'

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img scr="%s/%s" width="400px" height="400px" />'%(MEDIAURL, self.image))

    def image_tag_tiny(self):
        return mark_safe('<img scr="%s/%s" width="100px" height="100px" />'%(MEDIAURL, self.image))
    image_tag.short_description = 'Είκονα'

class Characteristics(models.Model):
    title =models.CharField(max_length=60,)

    def __str__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(unique=True,max_length=70,verbose_name='Τίτλος Κατηγορίας')
    description = models.TextField(null=True,blank=True, verbose_name='Περιγραφή')
    class Meta:
        ordering=['title']
        verbose_name="Κατηγορίες  "
    def __str__(self):
        return self.title

class TaxesCity(models.Model):
    title = models.CharField(max_length=64,unique=True)
    class Meta:
        verbose_name="ΔΟΥ   "
    def __str__(self):
        return self.title

class Supply(models.Model):
    title = models.CharField(unique=True, max_length=70, verbose_name="'Ονομα")
    afm = models.CharField(max_length=9, blank=True, null=True, verbose_name="ΑΦΜ")
    doy = models.ForeignKey(TaxesCity, verbose_name='Εφορία', null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True, verbose_name="Τηλέφωνο")
    phone1 = models.CharField(max_length=10, null=True, blank=True, verbose_name="Τηλέφωνο")
    fax = models.CharField(max_length=10, null=True, blank=True, verbose_name="Fax")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    balance = models.DecimalField(default=0, max_digits=100, decimal_places=2, verbose_name="Υπόλοιπο")
    site = models.CharField(max_length=40, blank=True, null=True, verbose_name='Site')
    address = models.CharField(max_length=40, null=True, blank=True, verbose_name='Διεύθυνση')
    description = models.TextField(null=True, blank=True, verbose_name="Περιγραφή")
    date_added = models.DateField(default=timezone.now)
    taxes_modifier = models.IntegerField(verbose_name='ΦΠΑ Τιμολογίου.', default=24)

    class Meta:
        verbose_name_plural = '9. Προμηθευτές'
        ordering = ['-title']

    #managing deposits
    remaining_deposit = models.DecimalField(default=0, decimal_places=2, max_digits=100, verbose_name='Υπόλοιπο προκαταβολών')

    def template_tag_remaining_deposit(self):
        return  ("{0:.2f}".format(round(self.remaining_deposit, 2))) + ' %s'%(CURRENCY)

    def template_tag_balance(self):
        return ("{0:.2f}".format(round(self.balance, 2))) + ' %s'%(CURRENCY)

    def __str__(self):
        return self.title

    def get_absolute_url_form(self):
        return reverse('edit_vendor_id',kwargs={'dk':self.id})

    def show_remain(self):
        return self.balance - self.remaining_deposit

class Costumers(models.Model):
    CHOICES = (('a','Retail'),
              ('b','Eshop'),
              ('c','PhoneRetail'),
              ('d','Stock')
              )
    title = models.CharField(unique=True, max_length=70,verbose_name="Ονομα/Επωνυμία")
    date_added = models.DateField(default=timezone.now)
    description = models.TextField(null=True,blank=True,verbose_name="Περιγραφή")
    phone = models.CharField(max_length=10,null=True,blank=True,verbose_name="Τηλέφωνο")
    phone1= models.CharField(max_length=10,null=True,blank=True,verbose_name="Τηλέφωνο")
    cellphone = models.CharField(max_length=10, null=True, blank=True, verbose_name='CellPhone')
    fax= models.CharField(max_length=10,null=True,blank=True,verbose_name="Fax")
    email = models.EmailField(null=True,blank=True,verbose_name="Email")
    zip_code = models.IntegerField(null=True, blank=True)
    site = models.CharField(max_length=40,blank=True,null=True, verbose_name='Site')
    address = models.CharField(max_length=40,null=True,blank=True,verbose_name='Διεύθυνση')
    balance = models.DecimalField(default=0,max_digits=10, decimal_places=3,verbose_name="Υπόλοιπο")
    afm = models.CharField(max_length=9,blank=True,null=True,verbose_name="ΑΦΜ")
    DOY = models.ForeignKey(TaxesCity,verbose_name='Εφορία',blank=True,null=True)
    category = models.CharField(default='a',choices=CHOICES, null=True, blank=True, max_length=1)

    def __str__(self):
        return self.title

class Color(models.Model):
    STATUS = (('a','Ενεργό'),('b','Μη Ενεργό'))
    title = models.CharField(max_length=64, unique=True, verbose_name='Ονομασία Χρώματος')
    status = models.CharField(max_length=1, default='a',choices=STATUS, verbose_name='Κατάσταση')
    code_id = models.CharField(max_length=25,blank=True,verbose_name='Κωδικός Χρώματος')

    class Meta:
        verbose_name_plural = '5. Χρώματα'

    def __str__(self):
        return self.title

class Size(models.Model):
    STATUS = (('a','Ενεργό'),('b','Μη Ενεργό'))
    title = models.CharField(max_length=64, unique=True, verbose_name='Ονομασία Μεγέθους')
    status = models.CharField(max_length=1, default='a',choices=STATUS, verbose_name='Κατάσταση')
    my_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['my_order', 'title']
        verbose_name_plural = '6. Μεγέθη'

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=120, verbose_name="'Ονομα προιόντος")
    order_code = models.CharField(null=True, blank=True, max_length=100, verbose_name="Κωδικός Τιμολογίου")
    price_buy = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Αγοράς") # the price which you buy the product
    category = models.ForeignKey(Category, blank=True, null=True)
    supplier = models.ForeignKey(Supply, verbose_name="Προμηθευτής", blank=True, null=True)
    wholesale_active = models.BooleanField(default=False, verbose_name="Υπερχονδρική")
    qty = models.DecimalField(default=0, verbose_name="Απόθεμα", max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=6, null=True, blank=True, verbose_name='Κωδικός/Barcode')
    order_discount = models.IntegerField(default=0, verbose_name="'Εκπτωση Τιμολογίου σε %")
    day_added = models.DateField( default=timezone.now, verbose_name='Ημερομηνία Δημιουργίας')
    qty_kilo = models.DecimalField(max_digits=5, decimal_places=3, default=1, verbose_name='Βάρος/Τεμάχια ανά Συσκευασία ')
    notes = models.TextField(null=True,blank=True, verbose_name='Περιγραφή')
    measure_unit = models.CharField(max_length=10, default='Τεμ.')
    safe_stock = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    objects= models.Manager()
    my_query = ProductManager()
    #site attritubes
    sku = models.CharField(max_length=50, blank=True, null=True)
    internet_description = models.TextField(blank=True, null=True)
    meta_description = models.CharField(max_length=300, null=True, blank=True)
    meta_keywords =  models.CharField(max_length=300, blank=True)
    ware_active = models.BooleanField(default=True, verbose_name='Ενεργοποίηση Προϊόντος')
    status = models.BooleanField(default=True, verbose_name='Κατάσταση Site')
    category_site = models.ForeignKey(CategorySite, blank=True, null=True)
    brand = models.ForeignKey(Brands, blank=True, null=True, verbose_name='Brand Name')
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    # price sell and discount sells
    price = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή λιανικής") #the price product have in the store
    margin= models.IntegerField(default=30, verbose_name='Margin', blank=True, null=True)
    markup = models.IntegerField(default=30, verbose_name='Markup', blank=True, null=True)
    price_internet= models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Internet(No use)")
    price_b2b= models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Χονδρικής") #the price product have in the website, if its 0 then website gets the price from store
    price_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Εκπτωτική Τιμή.')
    #size and color
    size = models.BooleanField(default=False, verbose_name='Μεγεθολόγιο')
    color = models.ForeignKey(Color, blank=True, null=True, verbose_name='Χρώμα')

    #site price on line 407 is  the final price of product
    class Meta:
        ordering = ['title']
        verbose_name_plural = "1. Προϊόντα"

    def check_identity(self):
        return 'product'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_page', kwargs={'slug': self.slug})

    def absolute_url_edit_product(self):
        return reverse('edit_product', kwargs={'dk': self.id})

    def tag_title(self):
        if self.color:
            return '%s, %s'%(self.title, self.color)
        return self.title

    def tag_category_site(self):
        msg = self.category_site if self.category_site else 'Δεν έχει επιλεχτεί κατηγορία'
        return msg

    def tag_brand(self):
        msg = self.brand if self.brand else 'Δεν έχει επιλεχτεί Brand'
        return msg

    @property
    def image(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_primary=True).last().image
        except:
            pass

    @property
    def image_back(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_back=True).last().image
        except:
            pass

    def have_size(self):
        return True if self.size else False

    @property
    def sizes(self):
        return SizeAttribute.objects.filter(product_related=self, qty__gte=1)

    def get_all_images(self):
        return ProductPhotos.objects.filter(active=True, product=self)
    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s%s" width="200px" height="200px">'%(MEDIAURL, self.image))
    def image_back_tag(self):
        if self.image_back:
            return mark_safe('<img src="%s%s" width="200px" height="200px">'%(MEDIAURL, self.image_back))
    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img src="%s%s" width="100px" height="100px">'%(MEDIAURL, self.image))
    def image_back_tag_tiny(self):
        if self.image_back:
            return mark_safe('<img src="%s%s" width="200px" height="200px">'%(MEDIAURL, self.image_back))
    def template_tag_price(self):
        if self.price_discount !=0:
            return '%s %s , %s %s' % (self.price_discount, CURRENCY, self.price, CURRENCY)
        return '%s %s' % (self.price, CURRENCY)

    def show_warehouse_remain(self):
        return self.qty * self.qty_kilo

    def check_safe_stock(self):
        current_stock = self.qty*self.qty_kilo
        if self.safe_stock == 0:
            return 'a'
        elif self.safe_stock >= current_stock:
            return 'b'
        else:
            return 'a'

    def final_price_warehouse(self):
        try:
            price_buy = float(self.price_buy)
            order_discount = float(self.order_discount)
            return float(price_buy * float((100 - order_discount)/100))
        except:
            return float(self.price_buy)

    def price_with_taxes(self):
        return (float(self.final_price_warehouse())* FPA)
    #check if discount exists
    def check_discount_on_sales(self):
        if self.price_discount == 0:
            return False
        return True

    def cost_of_remaining(self):
        try:
            return (self.qty/self.qty_kilo) * self.price_buy
        except:
            return self.qty*self.price_buy

    def markup_remaining(self):
        try:
            if self.cost_of_remaining():
                return Decimal(self.cost_of_remaining())*(1+Decimal(self.markup*0.01))
            else:
                return 0
        except:
            return (self.qty*self.price_buy)*(1+Decimal(self.markup*0.01))

    @property
    def site_price(self):
        discount_order = self.discount_set.all().filter(active=True, date_start__lt=datetime.datetime.now(), date_end__gt=datetime.datetime.now()).last()
        print(discount_order)
        #discount_order = self.discount_set.all().last() if self.discount_set.filter(active=True, date_start__gte=datetime.datetime.now(), date_end__lte=datetime.datetime.now()).exists() else None
        if discount_order:
            return round(self.price * (100-discount_order.value)/100 if discount_order.type_of_discount == 'a' else discount_order.value, 2)
        elif self.price_discount != 0:
            return self.price_discount
        else:
            return self.price

    def check_discount(self):
        dif = self.price - self.site_price
        if dif >0:
            return True
        return False

    def price_dif(self):
        dif = self.price - self.site_price
        if dif == self.price:
            dif = 0
        return dif

    @property
    def product_characteristics(self):
        instance = self
        return ProductCharacteristics.my_query.filter_by_instance(instance)

class CharacteristicsValue(models.Model):
    title = models.CharField(max_length=100)
    #related_to = models.CharField(blank=True,)


    def __str__(self):
        return self.title

class ProductCharManager(models.Manager):
    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(ProductCharManager, self).filter(content_type=content_type, object_id= obj_id)
        return qs

class ProductCharacteristics(models.Model):
    title = models.ForeignKey(Characteristics)
    description = models.ForeignKey(CharacteristicsValue)
    product_related = models.ForeignKey(Product, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id  = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id',)
    my_query = ProductCharManager()
    objects = models.Manager()
    focus = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '9. Χαρακτηριστικά Προϊόντος'

    def __str__(self):
        return str('%s - %s' %(self.title, self.description.title))

class RelatedProducts(models.Model):
    title = models.ForeignKey(Product, related_name='titleg')
    related = models.ManyToManyField(Product, related_name='relatedgproducts')

    class Meta:
        verbose_name_plural='7. Παρόμοια Προϊόντα'
    def __str__(self):
        return self.title.title

class SameColorProducts(models.Model):
    title = models.ForeignKey(Product, related_name='titlef')
    related = models.ManyToManyField(Product, related_name='relatedfproducts')

    class Meta:
        verbose_name_plural = '8. Ίδιο Χρώμα Προϊόντα'
    def __str__(self):
        return self.title.title

class SizeAttribute(models.Model):
    title = models.ForeignKey(Size)
    product_related = models.ForeignKey(Product, null=True)
    qty = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    order_discount = models.IntegerField(null=True, blank=True, default=0,verbose_name="'Εκπτωση Τιμολογίου σε %")
    price_buy = models.DecimalField(decimal_places=2,max_digits=6,default=0,verbose_name="Τιμή Αγοράς") # the price which you buy the product

    class Meta:
        verbose_name_plural = '2. Μεγεθολόγιο'

    def __str__(self):
        return '%s - %s'%(self.product_related,self.title)

    def check_product_in_order(self):
        return str(self.product_related + '. Χρώμα : ' + self.title.title + ', Μέγεθος : ' + self.title.title)

    def delete_update_product(self):
        self.product_related.qty -= self.qty
        self.product_related.save()

class ProductPhotos(models.Model):
    image = fields.ImageField(upload_to=product_directory_path, dependencies=[
        FileDependency(processor=ImageProcessor(
            format='JPEG', scale={'max_width': 800, 'max_height': 800}))
    ], )
    alt = models.CharField(null=True, blank=True, max_length=200, help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    title = models.CharField(null=True ,blank=True, max_length=100, help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    product = models.ForeignKey(Product)
    active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False, verbose_name='Αρχική Εικόνα')
    is_back = models.BooleanField(default=False, verbose_name='Δεύτερη Εικόνα')

    class Meta:
        verbose_name_plural = 'Gallery'

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img width="150px" height="150px" src="%s%s" />' %(MEDIAURL, self.image))
    image_tag.short_description = 'Εικονα'

    def image_tag_tiny(self):
        return mark_safe('<img width="150px" height="150px" src="%s%s" />' %(MEDIAURL, self.image))
    image_tag_tiny.short_description = 'Εικόνα'

#--------------------------------------------------------------------------------------------------

class ChangeQtyOrder(models.Model):
    title = models.CharField(max_length=64, unique=True, verbose_name='Σχολιασμός')
    day_added = models.DateField(auto_now=True)
    def __str__(self):
        return self.title

class ChangeQtyOrderItem(models.Model):
    title = models.ForeignKey(Product)
    order = models.ForeignKey(ChangeQtyOrder)
    qty = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    size = models.ForeignKey(SizeAttribute, blank=True, null=True)
    def show_product(self):
        return self.title

class ChangeQtyOrderItemSize(models.Model):
    title = models.ForeignKey(SizeAttribute)
    order = models.ForeignKey(ChangeQtyOrder)
    qty = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def show_product(self):
        return self.title
