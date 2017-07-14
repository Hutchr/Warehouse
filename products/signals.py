from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import slugify
from products.models import Product, CategorySite, Brands, ProductPhotos



@receiver(post_save, sender=Product)
def create_unique_slug_for_product(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify.slugify(instance.title)
        qs_exists = Product.objects.filter(slug=slug)
        if qs_exists.exists():
            slug = '%s-%s' %(slug, instance.id)
        instance.slug = slug
        instance.save()
post_save.connect(create_unique_slug_for_product, sender=Product)


def create_slug_cat_site(instance,new_slug=None):
    slug = slugify.slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs = CategorySite.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s'%(slug,qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

#brand
def create_slug_brand(instance, new_slug=None):
    slug = slugify.slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs = Brands.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s'%(slug,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug

def create_slug(instance, new_slug=None):
    slug = slugify.slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s'%(slug,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug


@receiver(post_save, sender=CategorySite)
def create_unique_slug_cs(sender, instance,*args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug_cat_site(instance)
        instance.save()
post_save.connect(create_unique_slug_cs, sender=CategorySite)

@receiver(post_save, sender=Brands)
def create_unique_slug_for_brands(sender, instance,*args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug_brand(instance)
        instance.save()
post_save.connect(create_unique_slug_for_brands, sender=Brands)


@receiver(post_save, sender=ProductPhotos)
def create_title_and_alt(sender, instance, *args, **kwargs):
    if not instance.title:
        instance.title = '%s' %(instance.product.title)
        instance.save()
    if not instance.alt:
        instance.alt = '%s' %(instance.product.title)
        instance.save()
post_save.connect(create_title_and_alt, sender=ProductPhotos)


from PoS.models import RetailOrder
@receiver(post_save, sender=RetailOrder)
def register_title(sender, instance, *args, **kwargs):
    remaining_value = instance.value - instance.paid_value
    if not instance.title:
        get_order_type = str(instance.get_order_type_display())
        get_count = RetailOrder.objects.filter(order_type = instance.order_type).count()
        instance.title = '%s-%s'%(get_order_type, get_count)
        instance.save()
    if instance.discount != remaining_value:
        instance.discount = remaining_value
        instance.save()
post_save.connect(register_title, sender=RetailOrder)


from blog.models import Post, PostCategory
def create_slug_post(instance, new_slug=None):
    slug = slugify.slugify(instance.title)
    #old method
    #text = unidecode.unidecode(instance.title).lower()
    #slug = slugify(text)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug,qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

@receiver(post_save, sender=Post)
def create_unique_slug_for_post(sender, instance,*args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug_post(instance)
        instance.save()
post_save.connect(create_unique_slug_for_post, sender=Post)

@receiver(post_save, sender=PostCategory)
def create_unique_slug_for_post_category(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify.slugify(instance.title)
        qs_exists = PostCategory.objects.filter(slug=slug)
        if qs_exists.exists():
            slug = '%s-%s' %(slug, instance.id)
        instance.slug = slug
        instance.save()
post_save.connect(create_unique_slug_for_post_category, sender=PostCategory)
