from django import forms
from products.models import *
from inventory_manager.models import *
from decimal import *

def update_product():
    pass


class VendorForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = '__all__'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['supplier','category','title','order_code','qty_kilo','price_buy','order_discount','price','price_internet','color','size']

class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def update_vendor(self, pk):
        final_price = self.cleaned_data.get('total_price')
        my_order = Order.objects.get(id=pk)
        vendor =my_order.vendor.title
        old_vendor =Supply.objects.get(title=vendor)
        new_vendor = self.cleaned_data.get('vendor')
        my_vendor = Supply.objects.get(title=new_vendor)
        balance = Order.objects.get(id=pk)
        bal = balance.total_price
        old_vendor.balance -= Decimal(bal)
        old_vendor.save()
        my_vendor.balance +=Decimal(final_price)
        my_vendor.save()

class OrderForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2050),))
    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['notes', 'total_price_no_discount', 'total_discount', 'total_price_after_discount', 'total_taxes',
                   'total_price','status','credit_balance', 'taxes_modifier']

    def update_vendor(self, pk):
        vendor = self.cleaned_data('vendor')
        my_vendor = Supply.objects.get(title=vendor)
        price = self.cleaned_data.get('total_price')

        my_order = Order.objects.get(id=pk)
        current_order = my_order.total_price
        currect_balance = my_vendor.balance
        f_price = (currect_balance + price) - current_order
        my_vendor.balance = f_price
        my_vendor.save()

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = "__all__"
        exclude = ['size', 'total_clean_value', 'total_value_with_taxes']

    def update_main_product(self, order_item):
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = int(self.cleaned_data.get('discount'))
        my_product = self.cleaned_data.get('product')
        taxes = self.cleaned_data.get('taxes')

        #update_product
        my_product.qty += qty
        my_product.price_buy = price
        my_product.order_discount = discount
        my_product.save()

        #update_order, vendor, and order item
        total_price = price * qty
        disc = (total_price * discount) / 100
        clean_value = total_price - disc
        taxes = (clean_value * (taxes)) / 100
        final_value = clean_value + taxes
        order = order_item.order
        vendor = order.vendor
        order.total_price_no_discount += total_price
        order.total_discount += disc
        order.total_price_after_discount += clean_value
        order.total_taxes += taxes
        order.total_price += final_value
        vendor.balance += final_value
        order_item.total_clean_value = clean_value
        order_item.total_value_with_taxes = final_value
        order_item.save()
        order.save()
        vendor.save()
        #update_vendor
        vendor = my_product.supplier

    def update_size(self, size):
        qty = self.cleaned_data.get('qty')
        size.qty += qty
        size.save()

    def modify_stock(self, mod):
        product = self.cleaned_data.get('product')
        my_product = Product.objects.get(title=product)
        qty = self.cleaned_data.get('qty')
        price = self.cleaned_data.get('price')
        discount = self.cleaned_data.get('discount')
        first_product = OrderItem.objects.get(id=mod)
        my_product.reserve += qty - first_product.qty
        my_product.price_buy = price
        my_product.ekptosi = discount
        my_product.save()

    def update_stock_and_vendor(self,pk):
        product = self.cleaned_data.get('product')
        my_product = Product.objects.get(title=product)
        qty = self.cleaned_data.get('qty')
        price = self.cleaned_data.get('price')
        discount = self.cleaned_data.get('discount')
        orderitem = OrderItem.objects.get(id=pk)
        order_taxes = orderitem.taxes
        order_taxes = dict(self.fields['taxes'].choices)[order_taxes]
        order_taxes = int(order_taxes)
        disc_float=((float(orderitem.discount))/100)*float(orderitem.price*orderitem.qty)
        final_price = ((Decimal(orderitem.price*orderitem.qty) - Decimal(disc_float))+ ((Decimal(orderitem.price*orderitem.qty) - (Decimal(disc_float)))* (Decimal(order_taxes)/100)))
        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes
        vendor =orderitem.order.vendor
        vendor.balance -= final_price
        vendor.balance += final_value
        vendor.save()
        my_product.reserve -= orderitem.qty
        my_product.reserve += qty
        my_product.price_buy = price
        my_product.ekptosi = discount
        my_product.save()

    def update_vendor(self, pk):
        final_price = self.cleaned_data.get('total_price')
        vendor = self.cleaned_data.get('vendor')
        my_vendor = Supply.objects.get(title = vendor)
        balance = Order.objects.get(id=pk)
        bal = balance.total_price
        print(bal)
        my_vendor.balance -= Decimal(bal)
        my_vendor.balance +=Decimal(final_price)
        my_vendor.save()

    def update_order(self, mod):
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = self.cleaned_data.get('discount')
        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes

        order = self.cleaned_data.get('order')
        orderitem = OrderItem.objects.get(id=mod)
        order_taxes = orderitem.taxes
        order_taxes = dict(self.fields['taxes'].choices)[order_taxes]
        order_taxes = int(order_taxes)

        my_order = Order.objects.get(code=order)

        my_order.total_price_no_discount -= Decimal(orderitem.price*orderitem.qty)
        my_order.total_price_no_discount += total_price


        disc_float =((float(orderitem.discount))/100)*float(orderitem.price*orderitem.qty)
        my_order.total_discount -= Decimal(disc_float)
        my_order.total_discount += disc

        my_order.total_price_after_discount -= (Decimal(orderitem.price*orderitem.qty) - Decimal(disc_float))
        my_order.total_price_after_discount += net_income


        my_order.total_taxes -= ((Decimal(orderitem.price*orderitem.qty) - (Decimal(disc_float)))* (Decimal(order_taxes)/100))
        my_order.total_taxes += taxes

        my_order.total_price -= ((Decimal(orderitem.price*orderitem.qty) - Decimal(disc_float))+ ((Decimal(orderitem.price*orderitem.qty) - (Decimal(disc_float)))* (Decimal(order_taxes)/100)))
        my_order.total_price += final_value


        my_order.save()

    #color and size section
    def update_order_size(self, order_item, size_id, qty):
        order_item.qty = qty
        exists = SizeAttribute.objects.get(title_id=size_id, product=order_item.product)
        if exists:
            order_item.size = exists
        else:
            create_SizeAttr = SizeAttribute.objects.create(title=Size.objects.get(id=size_id), product=order_item.product)
            create_SizeAttr.save()
            order_item.size = create_SizeAttr
        order_item.save()
        size = order_item.size
        size.qty += qty
        size.save()
        product = order_item.product
        product.qty += qty
        product.price_buy = order_item.price
        product.order_discount = order_item.discount
        product.save()

        total_price = order_item.price * qty
        disc = (total_price * order_item.discount) / 100
        net_income = total_price - disc
        order = order_item.order
        order.total_price_no_discount += total_price
        order.total_discount += disc
        order.total_price_after_discount += net_income
        taxes = order_item.taxes
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        taxes = (net_income * (fpa)) / 100
        order.total_taxes += taxes
        final_value = net_income + taxes
        order.total_price += final_value
        order.vendor.balance += final_value
        order.vendor.save()
        order.save()

    def add_to_product_with_color_and_size(self,order, product, color_attritube, size_attritube,):
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = self.cleaned_data.get('discount')

        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)

        product.ekptosi = discount
        product.price_buy = price
        product.reserve += qty
        product.save()

        color_attritube.price_buy = price
        color_attritube.qty += qty
        color_attritube.order_discount = discount
        color_attritube.save()

        size_attritube.price_buy = price
        size_attritube.qty += qty
        size_attritube.order_discount = discount
        size_attritube.save()

        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes


        my_order = order
        vendor = my_order.vendor.title
        my_vendor = Supply.objects.get(title=vendor)

        my_order.total_price_no_discount += total_price
        my_order.total_discount += disc
        my_order.total_price_after_discount += net_income
        my_order.total_taxes += taxes
        my_order.total_price += final_value
        my_vendor.balance += final_value
        my_order.save()
        my_vendor.save()

    def update_order_with_color_and_size(self, order, order_item):
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = self.cleaned_data.get('discount')

        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes


        orderitem = order_item
        order_taxes = orderitem.taxes
        order_taxes = dict(self.fields['taxes'].choices)[order_taxes]
        order_taxes = int(order_taxes)

        my_order = order
        my_order.total_price_no_discount -= Decimal(orderitem.price*orderitem.qty)
        my_order.total_price_no_discount += total_price


        disc_float =((float(orderitem.discount))/100)*float(orderitem.price*orderitem.qty)
        my_order.total_discount -= Decimal(disc_float)
        my_order.total_discount += disc

        my_order.total_price_after_discount -= (Decimal(orderitem.price*orderitem.qty) - Decimal(disc_float))
        my_order.total_price_after_discount += net_income


        my_order.total_taxes -= ((Decimal(orderitem.price*orderitem.qty) - (Decimal(disc_float)))* (Decimal(order_taxes)/100))
        my_order.total_taxes += taxes

        my_order.total_price -= ((Decimal(orderitem.price*orderitem.qty) - Decimal(disc_float))+ ((Decimal(orderitem.price*orderitem.qty) - (Decimal(disc_float)))* (Decimal(order_taxes)/100)))
        my_order.total_price += final_value


        my_order.save()

    def update_product_with_color_and_size(self, order, order_item):
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = self.cleaned_data.get('discount')
        product = self.cleaned_data.get('product')
        my_product = Product.objects.get(title=product)
        color = self.cleaned_data.get('color')
        size = self.cleaned_data.get('size')
        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes
        orderitem =order_item
        order_taxes = orderitem.taxes
        order_taxes = dict(self.fields['taxes'].choices)[order_taxes]
        order_taxes = int(order_taxes)
        disc_float=((float(orderitem.discount))/100)*float(orderitem.price*orderitem.qty)
        final_price = ((Decimal(orderitem.price*orderitem.qty) - Decimal(disc_float))+ ((Decimal(orderitem.price*orderitem.qty) - (Decimal(disc_float)))* (Decimal(order_taxes)/100)))
        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes
        vendor =orderitem.order.vendor
        vendor.balance -= final_price
        vendor.balance += final_value
        vendor.save()
        my_product.reserve -= orderitem.qty
        my_product.reserve += qty
        my_product.price_buy = price
        my_product.ekptosi = discount
        my_product.save()
        color.qty -= order_item.qty
        color.qty += qty
        color.price_buy = price
        color.order_discount = discount
        color.save()
        size.qty -= order_item.qty
        size.qty += qty
        size.price_buy = price
        size.order_discount = discount
        size.save()
    #only color section
    def add_to_product_with_only_color(self,order,  product, color_attritube, ):
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = self.cleaned_data.get('discount')

        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)

        product.ekptosi = discount
        product.price_buy = price
        product.reserve += qty
        product.save()

        color_attritube.price_buy = price
        color_attritube.qty += qty
        color_attritube.order_discount = discount
        color_attritube.save()


        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes

        my_order = order
        vendor = my_order.vendor.title
        my_vendor = Supply.objects.get(title=vendor)

        my_order.total_price_no_discount += total_price
        my_order.total_discount += disc
        my_order.total_price_after_discount += net_income
        my_order.total_taxes += taxes
        my_order.total_price += final_value
        my_vendor.balance += final_value
        my_order.save()
        my_vendor.save()

    def update_order_with_only_color(self, order, order_item):
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = self.cleaned_data.get('discount')
        product = self.cleaned_data.get('product')
        my_product = Product.objects.get(title=product)
        color = self.cleaned_data.get('color')
        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes
        orderitem =order_item
        order_taxes = orderitem.taxes
        order_taxes = dict(self.fields['taxes'].choices)[order_taxes]
        order_taxes = int(order_taxes)
        disc_float=((float(orderitem.discount))/100)*float(orderitem.price*orderitem.qty)
        final_price = ((Decimal(orderitem.price*orderitem.qty) - Decimal(disc_float))+ ((Decimal(orderitem.price*orderitem.qty) - (Decimal(disc_float)))* (Decimal(order_taxes)/100)))
        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]
        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes
        vendor =orderitem.order.vendor
        vendor.balance -= final_price
        vendor.balance += final_value
        vendor.save()
        my_product.reserve -= orderitem.qty
        my_product.reserve += qty
        my_product.price_buy = price
        my_product.ekptosi = discount
        my_product.save()

        color.qty -= order_item.qty
        color.qty += qty
        color.price_buy = price
        color.order_discount = discount
        color.save()

    def add_new_order_item(self):
        title = self.cleaned_data.get('product')
        price = self.cleaned_data.get('price')
        qty = self.cleaned_data.get('qty')
        discount = self.cleaned_data.get('discount')
        taxes = self.cleaned_data.get('taxes')
        taxes = dict(self.fields['taxes'].choices)[taxes]

        fpa = int(taxes)
        total_price = price * qty
        disc = (total_price * discount) / 100
        net_income = total_price - disc
        taxes = (net_income * (fpa)) / 100
        final_value = net_income + taxes
        order = self.cleaned_data.get('order')

        my_order = Order.objects.get(code=order)
        my_order.total_price_no_discount += total_price
        my_order.total_discount += disc
        my_order.total_price_after_discount += net_income
        my_order.total_taxes += taxes
        my_order.total_price += final_value

        my_vendor = Supply.objects.get(title =my_order.vendor.title)
        my_vendor.balance += Decimal(final_value)
        my_vendor.save()
        my_product = Product.objects.get(title=title)
        my_product.price_buy = price
        my_product.ekptosi = discount
        my_product.reserve += qty

        my_order.save()

class PayOrderFrom(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = PayOrders
        fields = '__all__'

    def update_order_and_vendor(self):
        value = self.cleaned_data.get('value')
        order = self.cleaned_data.get('title')
        value_of_portion = self.cleaned_data.get('value_portion')

        my_order = Order.objects.get(code=order)
        my_vendor = Supply.objects.get(title =order.vendor.title)


        if value_of_portion == 'a':
            my_order.status = 'a'
            my_order.credit_balance += Decimal(value)
            my_vendor.balance -=Decimal(value)
        elif value_of_portion == 'b':
            my_order.status ='d'
            my_order.credit_balance +=Decimal(value)
            my_vendor.balance -=Decimal(value)

        if my_order.credit_balance >= my_order.total_price:
            my_order.status ='a'
        my_vendor.save()
        my_order.save()

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

class DepositVendorForm(forms.ModelForm):
    #adds a new deposit to the vendor

    class Meta:
        model  = VendorDepositOrder
        fields = "__all__"


    def refresh(self,dk):
        value = self.cleaned_data.get('value')

        #updates vendor remaining deposit
        vendor = Supply.objects.get(id=dk)
        vendor.remaining_deposit += Decimal(value)
        vendor.save()

        #updates the PaymentMethod remaining
        payment_method = self.cleaned_data.get('payment_method')
        payment_method = PaymentMethod.objects.get(title = payment_method)
        payment_method.balance += Decimal(value)
        payment_method.save()

        if payment_method.payment_group:
            payment_method.payment_group.balance += Decimal(value)
            payment_method.payment_group.save()

        #updates

class PayOrderFormDeposit(forms.ModelForm):
    # use a portion of the remaining money or all to pay the orders
    day_added = forms.DateField(widget=forms.SelectDateWidget())

    class Meta:
        model = VendorDepositOrderPay
        fields = "__all__"

    def add_pay(self, order):
        value = self.cleaned_data.get('value')
        my_order = order
        my_vendor = order.vendor

        my_order.credit_balance += Decimal(value)
        my_vendor.balance -=Decimal(value)
        my_vendor.remaining_deposit -= Decimal(value)
        my_order.status = 'd'
        my_order.save()
        if my_order.credit_balance >= my_order.total_price:
            my_order.status = 'a'
        my_vendor.save()
        my_order.save()

class CheckOrderForm(forms.ModelForm):
    date_expire = forms.DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = CheckOrder
        fields = "__all__"


    def create_vendor_deposit_order(self):
        value = self.cleaned_data.get('value')
        vendor = self.cleaned_data.get('debtor')
        payment_method = self.cleaned_data.get('place')
        title = self.cleaned_data.get('title')


        new_order = VendorDepositOrder.objects.create(title=title, payment_method=payment_method, vendor =vendor, value=value)
        new_order.save()


        #updates vendor remaining deposit
        vendor = new_order.vendor
        vendor.remaining_deposit += Decimal(value)
        vendor.save()

        #updates the PaymentMethod remaining

        payment_method = PaymentMethod.objects.get(title = payment_method)
        payment_method.balance += Decimal(value)
        payment_method.save()

        if payment_method.payment_group:
            payment_method.payment_group.balance += Decimal(value)
            payment_method.payment_group.save()


    def edit(self, checkorder, form):
        #gets the old data

        old_price = checkorder.value
        old_place = checkorder.place
        old_status = checkorder.status
        old_debtor = checkorder.debtor

        #remove the old data
        '''
        old_place.balance -= Decimal(old_price)
        old_place.save()
        old_debtor.remaining_deposit -= Decimal(old_price)
        old_debtor.save()
        '''
        new_debtor = form.cleaned_data.get('debtor')
        new_price =form.cleaned_data.get('value')
        new_place = form.cleaned_data.get('place')
        new_status = form.cleaned_data.get('status')
        '''
        #add the new data
        new_place.balance += Decimal(new_price)
        new_place.save()
        new_debtor.remaining_deposit += Decimal(new_price)
        new_debtor.save()
        '''
        form.save()
        print(old_debtor.title,old_price, new_debtor.title,new_price)

class PaymentForm(forms.ModelForm):

    class Meta:
        model = PaymentMethod
        fields = "__all__"

class PaymentGroupForm(forms.ModelForm):

    class Meta:
        model = PaymentMethodGroup
        fields = "__all__"

class PreOrderForm(forms.ModelForm):

    class Meta:
        model = PreOrder
        fields = '__all__'

class PreOrderItemForm(forms.ModelForm):

    class Meta:
        model = PreOrderItem
        fields ='__all__'

class PreOrderNewItemForm(forms.ModelForm):

    class Meta:
        model = PreOrderNewItem
        fields ="__all__"

class PreOrderStatementItemForm(forms.ModelForm):

    class Meta:
        model= PreOrderStatementItem
        fields ="__all__"

class PreOrderStatementNewItemForm(forms.ModelForm):

    class Meta:
        model= PreOrderStatementNewItem
        fields ="__all__"