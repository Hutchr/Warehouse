from django import forms
from .models import *

#--------------------------------------Lianiki Section----------------------------------------------

class RetailEditForm(forms.ModelForm):
    class Meta:
        model = RetailOrder
        fields = '__all__'
        exclude = ['total_cost', 'paid_value', 'value', 'costumer', 'order_type', 'status', 'costumer_account',]

class RetailAddForm(forms.ModelForm):
    class Meta:
        model = RetailOrderItem
        fields = "__all__"
        exclude =['is_find', 'is_return']
    def add_item(self, order, product ):
        order = order
        if order.order_type == 'r':
            price = self.cleaned_data.get('price')
            cost = self.cleaned_data.get('cost')
            qty = self.cleaned_data.get('qty')
            if order.costumer_account:
                order.costumer_account.balance += price * qty
                order.costumer_account.total_order_value += price * qty
                order.costumer_account.save()
            #updates the order
            value = Decimal(price*qty)
            cost = Decimal(cost*qty)
            order.value += value
            order.total_cost += cost
            order.save()
            #updates the warehouse
            if product.qty_kilo != 0:
                product.qty -= qty/product.qty_kilo
                product.save()
            else:
                product.qty -= qty
                product.save()
        if order.order_type == 'b':
            price = self.cleaned_data.get('price')
            cost = self.cleaned_data.get('cost')
            qty = self.cleaned_data.get('qty')
            if order.costumer_account:
                order.costumer_account.balance -= price * qty
                order.costumer_account.total_order_value -= price * qty
                order.costumer_account.save()
            #updates the order
            value = Decimal(price*qty)
            cost = Decimal(cost*qty)
            order.value += value
            order.total_cost += cost
            order.save()
            #updates the warehouse
            if product.qty_kilo != 0:
                product.qty += qty/product.qty_kilo
                product.save()
            else:
                product.qty += qty
                product.save()

    def edit_item(self, order_item, old_price, old_qty, old_cost):
        if order_item.order.order_type == 'r' or order_item.order.order_type == 'e':
            old_total = old_price*old_qty
            old_cost = old_cost*old_qty
            order_item = order_item
            order = order_item.order
            price = self.cleaned_data.get('price')
            qty = self.cleaned_data.get('qty')
            cost = self.cleaned_data.get('cost')
            order_item.order.costumer_account.balance -= old_total
            order_item.order.costumer_account.balance += price*qty
            order_item.order.costumer_account.paid_value -= old_total
            order_item.order.costumer_account.paid_value += price*qty
            order_item.order.costumer_account.total_order_value -= old_total
            order_item.order.costumer_account.total_order_value += price*qty
            order_item.order.costumer_account.save()
            #update the order
            order.value -= Decimal(old_total)
            order.value += Decimal(price*qty)
            order.total_cost -= Decimal(old_cost)
            order.total_cost += Decimal(cost*qty)
            order.save()

            #update the warehouse
            product = order_item.title
            if product.qty_kilo != 0:
                product.qty += old_qty/product.qty_kilo
                product.qty -= qty/product.qty_kilo
                product.save()
            else:
                product.qty += old_qty
                product.qty -= qty
                product.save()
            if order_item.size:
                order_item.size.qty += old_qty
                order_item.size.qty -= qty
                order_item.size.save()

        if order_item.order.order_type == 'b':
            old_total = old_price*old_qty
            old_cost = old_cost*old_qty
            order_item = order_item
            order = order_item.order
            price = self.cleaned_data.get('price')
            qty = self.cleaned_data.get('qty')
            cost = self.cleaned_data.get('cost')
            order_item.order.costumer_account.balance += old_total
            order_item.order.costumer_account.balance -= price*qty
            order_item.order.costumer_account.paid_value += old_total
            order_item.order.costumer_account.paid_value -= price*qty
            order_item.order.costumer_account.total_order_value += old_total
            order_item.order.costumer_account.total_order_value -= price*qty
            order_item.order.costumer_account.save()
            #update the order
            order.value -= Decimal(old_total)
            order.value += Decimal(price*qty)
            order.total_cost -= Decimal(old_cost)
            order.total_cost += Decimal(cost*qty)
            order.save()

            #update the warehouse
            product = order_item.title
            if product.qty_kilo != 0:
                product.qty -= old_qty/product.qty_kilo
                product.qty += qty/product.qty_kilo
                product.save()
            else:
                product.qty -= old_qty
                product.qty += qty
                product.save()
            if order_item.size:
                order_item.size.qty -= old_qty
                order_item.size.qty += qty
                order_item.size.save()

class RetailForm(forms.ModelForm):
    class Meta:
        model= RetailOrder
        fields = '__all__'
        exclude = ['total_cost','paid_value', 'value', 'costumer', 'order_type', 'status', 'costumer_account', ]

class EshopEditForm(forms.ModelForm):
    class Meta:
        model = RetailOrder
        fields = '__all__'
        exclude = ['order_type', 'day_created', 'total_cost', 'seller_account', 'eshop_order_id', 'eshop_session_id', 'day_sent' ]

class PayRetailForm(forms.ModelForm):
    class Meta:
        model = RetailOrder
        fields =['paid_value']

'''
class RetailDiscountForm(forms.ModelForm):
    class Meta:
        model = Lianiki_Order
        fields = ['discount']

    def value_after_discount(self, lianiki_order, old_discount):
        new_discount = self.cleaned_data.get('discount')
        current_discount = new_discount - old_discount
        lianiki_order.value -= current_discount
        lianiki_order.save()
        lianiki_order.costumer_account.balance -= current_discount
        lianiki_order.costumer_account.save()

class EshopOrderForm(forms.ModelForm):

    class Meta:
        model = Lianiki_Order
        fields = '__all__'
        exclude = ['status', 'value', 'paid_value', 'total_cost']

class LianikiForm(forms.ModelForm):

    class Meta:
        model= Lianiki_Order
        fields = '__all__'
        exclude = ['total_cost','paid_value', 'value', 'costumer', 'order_type', 'status', 'costumer_account', ]

class LianikiAddItemForm(forms.ModelForm):
    class Meta:
        model = LianikiOrderItem
        fields ="__all__"
        exclude =['is_find',]
    def add_item(self, order, product ):
        order = order
        price = self.cleaned_data.get('price')
        cost = self.cleaned_data.get('cost')
        qty = self.cleaned_data.get('qty')
        if order.costumer_account:
            order.costumer_account.balance += price * qty
            order.costumer_account.save()

        #updates the order
        value = Decimal(price*qty)
        cost = Decimal(cost*qty)
        order.value += value
        order.total_cost += cost
        order.save()

        #updates the warehouse
        if product.qty_kilo != 0:
            product.reserve -= qty/product.qty_kilo
            product.save()
        else:
            product.reserve -= qty
            product.save()




    def edit_item(self,pk):
        order_item = LianikiOrderItem.objects.get(id= pk)
        order = order_item.order
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        cost = self.cleaned_data.get('cost')

        order_item.order.costumer_account.balance -= order_item.price*order_item.qty
        order_item.order.costumer_account.balance += price*qty
        order_item.order.costumer_account.save()
        #update the order
        order.value -= Decimal(order_item.price*order_item.qty)
        order.value += Decimal(price*qty)
        order.total_cost -=Decimal(order_item.cost*order_item.qty)
        order.total_cost += Decimal(cost*qty)
        order.save()

        #update the warehouse
        product = order_item.title
        if product.qty_kilo != 0:
            product.reserve += order_item.qty/product.qty_kilo
            product.qty -= qty/product.qty_kilo
            product.save()
        else:
            product.qty += order_item.qty
            product.reserve -= qty
            product.save()

        if order_item.color:
            order_item.color.qty +=order_item.qty
            order_item.color.qty -= qty
            order_item.color.save()
        if order_item.size:
            order_item.size.qty += order_item.qty
            order_item.size.qty -= qty
            order_item.size.save()
'''
class DestroyOrderForm(forms.ModelForm):

    class Meta:
        model = DestroyOrder
        fields ='__all__'

class DestroyOrderItemForm(forms.ModelForm):

    class Meta:
        model =DestroyOrderItem
        fields ='__all__'


    def update_order_and_warehouse(self, order, product):
        order = order
        product = product
        qty = self.cleaned_data.get('qty')
        cost = self.cleaned_data.get('cost')
        try:
            product.qty -= qty/product.qty_kilo
            product.save()
        except:
            product.qty -= qty
            product.save()
        order.total_cost += qty*cost
        order.save()


    def edit_order_and_warehouse(self,dk,pk):
        order = DestroyOrder.objects.get(id=dk)
        order_item = DestroyOrderItem.objects.get(id=pk)
        old_cost = order_item.qty*order_item.cost

        new_qty = self.cleaned_data.get('qty')
        new_cost = self.cleaned_data.get('cost')
        new_cost = new_qty*new_cost

        #updates destroy_order
        total_cost = new_cost-old_cost
        order.total_cost += total_cost



        total_qty = new_qty - order_item.qty

        order.save()

class ReturnItemChooseQty(forms.Form):
    qty = forms.IntegerField(required=True,)

#will be deleted from here


class ReturnOrderForm(forms.ModelForm):
    class Meta:
        model = RetailOrderItem
        fields ='__all__'

class ReturnOrderItemForm(forms.ModelForm):
    class Meta:
        model = RetailOrderItem
        fields ='__all__'

    def update_order_and_warehouse(self,order,product):
        order = order
        product = product
        qty = self.cleaned_data.get('qty')
        cost = self.cleaned_data.get('cost')
        value = self.cleaned_data.get('price')

        try:
            product.reserve += qty/product.qty_kilo
            product.save()
        except:
            product.reserve += qty
            product.save()

        order.cost += qty*cost
        order.value += qty*value
        order.save()


    def edit_order_and_warehouse(self,dk,pk):
        order = RetailReturnOrder.objects.get(id=dk)
        order_item = RetailReturnItem.objects.get(id=pk)
        old_cost = order_item.qty*order_item.cost
        old_price = order_item.qty*order_item.price

        new_qty = self.cleaned_data.get('qty')
        new_cost = self.cleaned_data.get('cost')
        new_price = self.cleaned_data.get('price')
        new_cost = new_qty*new_cost
        new_price = new_qty*new_price

        #updates destroy_order
        total_cost = new_cost-old_cost
        total_price = new_price -old_price
        order.cost += total_cost
        order.value += total_price


        #updates warehouse
        product = order_item.title
        print(order_item.qty)
        total_qty = new_qty - order_item.qty
        product.qty += total_qty
        product.save()
        order.save()


