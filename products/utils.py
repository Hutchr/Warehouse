from .models import *
from inventory_manager.models import *




def show_avg_per_cat():
    cat = Category.objects.all().count()
    products = Product.objects.count()
    if cat ==0:
        return 0
    else:
        return products/cat

def show_avg_per_vendor():
    cat = Supply.objects.all().count()
    products = Product.objects.count()
    if cat ==0:
        return 0
    else:
        return products/cat

def show_avg_per_order():
    cat = Order.objects.all().count()
    products = Product.objects.count()
    if cat ==0:
        return 0
    else:
        return products/cat