from django.contrib import admin
from import_export. admin import ImportExportModelAdmin
from .models import *
# Register your models here.

class OrderAdmin(ImportExportModelAdmin):
    pass

class OrderItemAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Unit)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(PayOrders)
admin.site.register(PaymentMethod)
admin.site.register(PaymentMethodGroup)

admin.site.register(PreOrderStatement)
admin.site.register(PreOrderStatementItem)

admin.site.register(VendorDepositOrderPay)