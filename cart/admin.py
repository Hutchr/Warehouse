from django.contrib import admin
from .models import *
# Register your models here.


class VoucherAdmin(admin.ModelAdmin):
    list_display = ['title', 'coupon_code', 'type_of_discount', 'price', 'date_start', 'date_end', 'active']
    list_filter = ['active', 'type_of_discount']

class CartRulesAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(CartItem)
admin.site.register(Voucher, VoucherAdmin)
admin.site.register(CartRules, CartRulesAdmin)