from django.db import models
from django.contrib.auth.models import User
from products.models import CategorySite
from django.utils.safestring import mark_safe
# Create your models here.

def upload_file(instance, filename):
    return 'recipes/%s/%s'%(instance.title, filename)

#MEDIAURL = 'media'
MEDIAURL = 'https://monastiraki.s3.amazonaws.com/media'

class CompanyInfo(models.Model):
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    zip_code = models.IntegerField()
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    phone = models.IntegerField()
    currency = models.CharField(max_length=3, default='€')
    class Meta:
        verbose_name_plural = 'Πληροφορίες Καταστήματος'
    def __str__(self):
        return self.title

class SiteSettings(models.Model):
    title = models.CharField(default='default', unique=True, max_length=50)
    #first_page
    last_products_qty = models.IntegerField(default=20)
    show_products_with_qty = models.BooleanField(default=False)
    show_products_site_active = models.BooleanField(default=True)
    show_products_ware_active = models.BooleanField(default=True)
    default_months_for_report = models.IntegerField(default=1)

    def __str__(self):
        return self.title

class EshopInformation(models.Model):
    title = models.CharField(max_length=100, verbose_name="Όνομα Εταιρίας")
    address = models.TextField(null=True, blank=True, help_text='For the contact page')
    call_center = models.TextField(null=True, blank=True, help_text='For the contact page')
    support = models.TextField(null=True, blank=True, help_text='For the contact page')
    info_text = models.TextField(null=True, help_text='url: info_eshop')
    class Meta:
        verbose_name_plural = 'Πληροφορίες για την Contact Page'

    def __str__(self):
        return self.title

class EshopAskQuestions(models.Model):
    title = models.CharField(max_length=100)
    number = models.IntegerField(default=1)
    content = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    class Meta:
        ordering=['number']
        verbose_name_plural = 'FAQ'

    def __str__(self):
        return self.title

class WelcomePage(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=128,verbose_name='Ονομασία Site')
    logo = models.ImageField(upload_to=upload_file, blank=True, help_text='139*60')
    logo_small = models.ImageField(upload_to=upload_file, blank=True, help_text='93*60')
    #upper section
    phone_number = models.CharField(max_length=10)
    phone_title_pop = models.CharField(max_length=100, blank=True, help_text='Its the title of the popup on phone nav bar')
    phone_content_pop = models.TextField(max_length=100, help_text='The content')
    info = models.CharField(max_length=100, blank=True, )
    info_title_pop = models.CharField(max_length=100, blank=True, help_text='navbar info title')
    info_content_pop = models.TextField(max_length=100,help_text='navbar info content')
    login_text = models.CharField(max_length=100, blank=True)
    sign_in_text = models.CharField(max_length=100, blank=True)
    signed_in_text = models.CharField(max_length=100, blank=True)
    order_text = models.CharField(max_length=100, blank=True)
    seo_keywords = models.CharField(max_length=160, blank=True, null=True)
    seo_description = models.CharField(max_length=160, blank=True, null=True)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = '1.Διαχείριση Αρχικής Σελίδας'
    def logo_tag(self):
        return mark_safe("<img src='%s/%s' width='250px' height='250px' />"%(MEDIAURL, self.logo))
    logo_tag.short_description = 'Logo'
    def logo_small_tag(self):
        return mark_safe("<img src='%s/%s' width='250px' height='250px' />"%(MEDIAURL, self.logo_small))
    logo_tag.short_description = 'Logo small'

class OfferPage(models.Model):
    active = models.BooleanField(default=True, verbose_name='Ενεργό')
    page_related = models.ForeignKey(WelcomePage, null=True)
    title = models.CharField(max_length=50, verbose_name='Tίτλος')
    text = models.CharField(max_length=200, verbose_name='Link')
    href = models.URLField(verbose_name='URL')
    class Meta:
        verbose_name_plural='2. Ανακοίνωση Προσφοράς'

    def __str__(self):
        return self.title

class UserTerms(models.Model):
    title = models.CharField(max_length=120)
    text = models.TextField()
    priority = models.IntegerField(default=1)
    related_to = models.ForeignKey(WelcomePage)

    def __str__(self):
        return self.title

class Banners(models.Model):
    active = models.BooleanField(default=True)
    STATUS = (('a','active'),('b','Inactive'))
    title = models.CharField( max_length=128, blank=True, null=True)
    alt = models.CharField( max_length=128, blank=True, null=True)
    image = models.ImageField(upload_to=upload_file, help_text='900px * 420px')
    width = models.DecimalField(default=300, decimal_places=1, max_digits=5)
    height = models.DecimalField(default=200, decimal_places=1, max_digits=5)
    status = models.CharField(default='a',max_length=1, choices=STATUS)
    href = models.CharField(max_length=500, null=True, blank=True)
    page_related = models.ForeignKey(WelcomePage, null=True)
    class Meta:
        verbose_name_plural = '3. Banner'
    def __str__(self):
        return self.title
    def image_tag(self):
        return mark_safe("<img src='%s/%s' width='600px' height='300px' />"%(MEDIAURL, self.image))
    image_tag.short_description = 'Εικόνα'
    def image_tag_tiny(self):
        return mark_safe("<img src='%s/%s' width='200px' height='100px' />"%(MEDIAURL, self.image))
    image_tag.short_description = 'Εικόνα'

class SecondSectionBanners(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField( max_length=128)
    alt = models.CharField( max_length=128)
    image = models.ImageField(upload_to=upload_file, help_text='908px * 410px')
    href = models.CharField(max_length=500, null=True, blank=True)
    page_related = models.ForeignKey(WelcomePage, null=True)
    class Meta:
        verbose_name_plural='5. Δεύτερα Banners'

    def __str__(self):
        return self.title
    def image_tag(self):
        return mark_safe("<img src='%s/%s' width='600px' height='300px' />"%(MEDIAURL, self.image))
    image_tag.short_description = 'Εικόνα'
    def image_tag_tiny(self):
        return mark_safe("<img src='%s/%s' width='200px' height='100px' />"%(MEDIAURL, self.image))
    image_tag.short_description = 'Εικόνα'

class FrontPageMessages(models.Model):
    title = models.CharField(max_length=100)
    style_of = models.CharField(max_length=100, help_text='announcement,information,success,warning,error')
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    page_related = models.ForeignKey(WelcomePage, null=True)
    class Meta:
        verbose_name_plural ='4. Μήνυμα Αρχικής Σελίδας'

    def __str__(self):
        return self.title

class Footer(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(default='default', unique=True, max_length=100)
    category_name_1 = models.CharField(max_length=100)
    pick_category_1 = models.ManyToManyField(CategorySite, blank=True, null=True)
    category_name_2 = models.CharField(max_length=100)
    page_related = models.ForeignKey(WelcomePage, null=True)
    class Meta:
        verbose_name_plural= '6. Footer'
    def __str__(self):
        return self.title

class FooterCategory(models.Model):
    title = models.ForeignKey(CategorySite, unique=True)
    footer = models.ForeignKey(Footer)
    def __str__(self):
        return self.title.title

class Gallery(models.Model):
    title = models.CharField(max_length=50, default='Το Μοναστηράκι')
    alt = models.CharField(max_length=50, default='Το Μοναστηράκι')
    image = models.ImageField(upload_to=upload_file)

    def __str__(self):
        return self.title