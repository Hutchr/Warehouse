from django.contrib import admin
from .models import *

# Register your models here.
class RetailItemInline(admin.TabularInline):
    model = RetailOrderItem
    extra = 2

class RetailOrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'qty', 'price', 'size', 'is_find']
    list_filter = ['is_find']
    search_fields = ['title', 'size', 'order']


class RetailAdmin(admin.ModelAdmin):
    list_display = ['day_created', 'title', 'status', 'value', 'costumer_account']
    list_filter =['status', 'order_type']
    search_fields = ['title', 'costumer_account', ]
    inlines = [RetailItemInline,]
    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields':(('title', 'value', 'order_type'), ('status', 'payment_method',), 'day_created'),
        }),
        ('Τιμές', {
            'fields':(('shipping', 'shipping_cost', 'discount', 'value', 'paid_value'), ),
        }),
        ('Στοιχεία Πελάτη', {
            'fields':(('first_name', 'last_name', 'email'), ('address', 'city', 'state', 'zip_code'), ('phone', 'cellphone'),'costumer_account'),
        }),
        ('Γενικές Πληροφορίες', {
            'fields':(('notes', 'eshop_session_id', 'eshop_order_id'),)
        })


    )

admin.site.register(RetailOrder, RetailAdmin)
admin.site.register(RetailOrderItem, RetailOrderAdmin)

admin.site.register(Shipping)
admin.site.register(Order_status)







