from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ToolsTableOrder

@receiver(post_save, sender=ToolsTableOrder)
def maximum_order(sender, instance, *args, **kwargs):
    if instance.show_number_of_products > 50:
        instance.show_number_of_products = 50
        instance.save()
post_save.connect(maximum_order, sender=ToolsTableOrder)