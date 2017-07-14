from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Banners, WelcomePage, SecondSectionBanners


@receiver(post_save, sender=Banners)
def create_title_and_alt(sender, instance, *args, **kwargs):
    welcome_page_exists = WelcomePage.objects.filter(active=True)
    if welcome_page_exists:
        get_welcome_page = welcome_page_exists.last()
        if not instance.title:
            instance.title = get_welcome_page.title
            instance.save()
        if not instance.alt:
            instance.alt = get_welcome_page.title
            instance.save()
post_save.connect(create_title_and_alt, sender=Banners)


@receiver(post_save, sender=SecondSectionBanners)
def create_title_and_alt_second(sender, instance, *args, **kwargs):
    welcome_page_exists = WelcomePage.objects.filter(active=True)
    if welcome_page_exists:
        get_welcome_page = welcome_page_exists.last()
        if instance.title is None:
            instance.title = get_welcome_page.title
            instance.save()
        if instance.alt is None:
            instance.alt = get_welcome_page.title
            instance.save()
post_save.connect(create_title_and_alt_second, sender=SecondSectionBanners)

