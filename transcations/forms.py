from django import forms
from .models import *
from decimal import Decimal

class LogForm(forms.ModelForm):
    #Creates a new Order payment for the Log_categories
    date = forms.DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = Order_Fixed_Cost
        fields = "__all__"
        exclude =['credit_balance','active']


    def sum_up(self,dk):
        order = Order_Fixed_Cost.objects.all().last()
        log = Fixed_Costs_item.objects.get(id=dk)
        log2 = Fixed_costs.objects.get(title = log.category)
        log.total_dept += order.price
        log.save()
        log2.total_dept += order.price
        log2.save()





    def edit(self,dk,pk):
        order = Order_Fixed_Cost.objects.get(id=pk)
        log = Fixed_Costs_item.objects.get(id=dk)
        log2 = Fixed_costs.objects.get(title = log.category)

        actual_price = self.cleaned_data.get('price')

        log.total_dept -= Decimal(order.price)
        log.total_dept += Decimal(actual_price)
        log.save()

        log2.total_dept -= Decimal(order.price)
        log2.total_dept += Decimal(actual_price)
        log2.save()


class LogFormCate(forms.ModelForm):
    #Create a New LogCategory.
    class Meta:
        model =Fixed_Costs_item
        fields = ['title','category']



class PayLogForm(forms.ModelForm):
    #pay the LogForm Order and updates everything
    date = forms.DateField(widget=forms.SelectDateWidget())
    class Meta:
        model =PayOrderFixedCost
        fields="__all__"


    def pay(self,dk):
        
        pay_order = PayOrderFixedCost.objects.all().last()
        order_cost = Order_Fixed_Cost.objects.get(id=dk)

        order_cost.credit_balance += pay_order.price
        order_cost.save()
        
        log = order_cost.category.title
        log = Fixed_Costs_item.objects.get(title=log)
        
        log2 = log.category.title
        log2 = Fixed_costs.objects.get(title = log2)


        if pay_order.price-order_cost.credit_balance >0:
            log.total_pay += pay_order.price
            log.save()
            log2.total_pay += pay_order.price
            log2.save()

        else:
            order_cost.active = 'b'
            order_cost.save()
            log.total_pay += pay_order.price
            log.save()
            log2.total_pay += pay_order.price
            log2.save()


class PersonForm(forms.ModelForm):
    date_joined = forms.DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = Person
        fields ="__all__"
        exclude = ['hour_salary_sum','salary_remaining','total_amount_paid','salary_paid']


class OccupationForm(forms.ModelForm):

    class Meta:
        model =Occupation
        fields ="__all__"


class CreateFormBasicSalary(forms.ModelForm):

    class Meta:
        model = CreatePersonSalaryCost
        fields = "__all__"
        exclude =['status','paid_value']

    def add_salary(self, dk, pk):

        price = self.cleaned_data.get('value')
        category = Occupation.objects.get(id=dk)
        category.total_cost += Decimal(price)
        category.save()

        person = Person.objects.get(id=pk)
        person.total_amount_paid += Decimal(price)
        person.salary_paid +=Decimal(price)
        person.save()

        type_  = self.cleaned_data.get('category')
        type_pay = CategoryPersonPay.objects.get(title =type_)
        type_pay.remaining_cost += Decimal(price)
        type_pay.total_cost += Decimal(price)
        type_pay.save()

    def edit_people_order(self,dk,pk,ok):
        order_pay = CreatePersonSalaryCost.objects.get(id=ok)
        price = self.cleaned_data.get('value')

        #updates the occupation of the person
        category = Occupation.objects.get(id=dk)
        category.total_cost -= order_pay.value
        category.total_cost += Decimal(price)
        category.save()

        #updates the person
        person = Person.objects.get(id=pk)
        person.total_amount_paid -= order_pay.value
        person.salary_paid -= order_pay.value
        person.total_amount_paid += Decimal(price)
        person.salary_paid += Decimal(price)
        person.save()

        #updates the type of pay
        type_  = self.cleaned_data.get('category')
        type_pay = CategoryPersonPay.objects.get(title =type_)
        type_pay.remaining_cost -= order_pay.value
        type_pay.total_cost -= order_pay.value
        type_pay.remaining_cost += Decimal(price)
        type_pay.total_cost += Decimal(price)
        type_pay.save()

        date = self.cleaned_data.get('day_expire')
        order_pay.day_expire = date
        order_pay.save()

class PersonPayFormSalaryCost(forms.ModelForm):

    class Meta:
        model = PayPersonSalaryCost
        fields ='__all__'

    def salary_pay(self, dk, pk):
        price = self.cleaned_data.get('value')
        person = Person.objects.get(id=dk)

        category = Occupation.objects.get(title = person.occupation)
        category.remaining_cost -= Decimal(price)
        category.save()
        category.category.total_pay += Decimal(price)
        category.category.save()

        person.salary_paid -= Decimal(price)
        person.save()

        category_pay = self.cleaned_data.get('category')
        cat = CategoryPersonPay.objects.get(title=category_pay)
        cat.remaining_cost -= Decimal(price)
        cat.save()


        myorder =  CreatePersonSalaryCost.objects.get(id=pk)
        myorder.paid_value += Decimal(price)
        myorder.save()

        myorder2 = CreatePersonSalaryCost.objects.get(id=pk)
        if myorder2.paid_value >= myorder.value:
            myorder2.status = 'b'
            myorder2.save()




#-----------------------------PagiaExoda---------------------------------------------------------------------------------------



class PagiaExodaOrderForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = Pagia_Exoda_Order
        fields = "__all__"
        exclude =['credit_balance','active']

    def sum_up(self,dk):
        data = self.cleaned_data.get('price')
        person_name = self.cleaned_data.get('person')
        person = PersonMastoras.objects.get(title =person_name)

        data = Decimal(data)
        person.remaining_cost += data
        person.total_cost += data
        person.save()

        log_id = Pagia_Exoda.objects.get(id=dk)
        log_id.total_cost += data
        log_id.save()

        log_id.category.total_dept += data
        log_id.category.save()




class PagiaExodaPayOrderForm(forms.ModelForm):

    class Meta:
        model = Pagia_Exoda_Pay_Order
        fields = "__all__"


    def sums_up(self,dk,pk):
        pagia_exoda = Pagia_Exoda.objects.get(id=dk)
        pagia_order = Pagia_Exoda_Order.objects.get(id=pk)
        person = pagia_order.person
        value = self.cleaned_data.get('value')
        value =Decimal(value)
        
        pagia_exoda.remaining_cost += value
        pagia_exoda.save()

        pagia_exoda.category.total_pay +=Decimal(value)
        pagia_exoda.category.save()
        
        pagia_order.credit_balance += value
        pagia_order.save()
        
        person.remaining_cost -= Decimal(value)

        person.save()
        
        
        
        pagia_order_balance =pagia_order.show_remain()
        if pagia_order_balance <= 0:
            pagia_order.active = 'b'
            pagia_order.save()
        




class PagiaExodaOrderEditForm(forms.ModelForm):

    class Meta:
        model = Pagia_Exoda_Order
        fields = "__all__"

    def edit_order(self, category ,order):

        old_value = order.price
        old_value = Decimal(old_value)
        old_person = order.person

        old_person.remaining_cost -= old_value
        old_person.total_cost -= old_value
        old_person.save()

        old_log = category
        old_log.total_cost -= old_value
        old_log.category.total_dept -= old_value
        old_log.save()


        data = self.cleaned_data.get('price')
        person_name = self.cleaned_data.get('person')
        person = PersonMastoras.objects.get(title =person_name)


        data = Decimal(data)
        person.remaining_cost += data
        person.total_cost += data
        person.save()

        log_id = category
        log_id.total_cost += data
        log_id.save()

        log_id.category.total_dept += data
        log_id.category.save()










class PersonMastorasForm(forms.ModelForm):

    class Meta:
        model= PersonMastoras
        fields = "__all__"
        exclude = ['remaining_cost','total_cost']
        
        
        








