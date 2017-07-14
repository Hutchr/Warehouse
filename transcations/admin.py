from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Fixed_costs)
admin.site.register(Fixed_Costs_item)
admin.site.register(Order_Fixed_Cost)
admin.site.register(PayPersonSalaryCost)

admin.site.register(Occupation)
admin.site.register(Person)
admin.site.register(CategoryPersonPay)
admin.site.register(CreatePersonSalaryCost)
admin.site.register(Pagia_Exoda)
admin.site.register(Pagia_Exoda_Order)
admin.site.register(PersonMastoras)
