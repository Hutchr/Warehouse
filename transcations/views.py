from django.shortcuts import render,HttpResponseRedirect
from django.contrib import messages
from django.db.models import Q
from inventory_manager.models import *
from .models import *
from inventory_manager.form import *
from django.template.context_processors import csrf
from .forms import *
from django.utils import timezone
import datetime

# Create your views here.

def homepage(request):
    title ='Πληρωμές'
    orders1 = Order.objects.all().filter(status='p').order_by('date')[0:4]
    pagia = Pagia_Exoda_Order.objects.filter(active='a')[0:5]
    person_log = CreatePersonSalaryCost.objects.all().filter(status ='a')[0:5]

    start_date = datetime.date.today()
    end_date = datetime.date.today() + datetime.timedelta(days=3)
    start_date_end =datetime.date.today() -  datetime.timedelta(days=30)

    log_end = Order_Fixed_Cost.objects.all().filter(date__range=[str(start_date),str(end_date)])

    log = Order_Fixed_Cost.objects.all().filter(date__range=[str(start_date),str(end_date)])


    context ={
        'title':title,
        'log':log,
        'orders1':orders1,

        'pagia':pagia,
        'person_log':person_log,
    }
    return render(request,'inventory/pay_section/pay_homepage.html', context)


def pay_order_section(request):
    #main page that show all remaining orders
    orders = Order.objects.all().filter(
         Q(status='d')|
         Q(status='p')).distinct().order_by('-day_created')
    title = 'Αποπληρωμή Τιμολογίων'
    context = {
        'title': title,
        'orders':orders,
    }
    return render(request, 'inventory/pay_section/pay_orders.html', context)

def pay_order_from_deposit(request, dk):
    title = 'Υπόλοιπο Προκαταβολών'
    orders = Order.objects.all().filter(
         Q(status='d')|
         Q(status='p')).distinct().order_by('-day_created')
    order = Order.objects.get(id=dk)
    vendor_remaining = order.vendor.remaining_deposit
    if order.ipoloipo_xreostiko() > vendor_remaining:
        messages.warning(request,'Δεν υπάρχει διαθέσιμο υπόλοιπο για την πληρωμή του τιμολογίου %s'%(order.code))
        return HttpResponseRedirect('/πληρωμές-εισπράξεις/αποπληρωμές-τιμολογίων/')
    if request.POST:
        form = PayOrderFormDeposit(request.POST,)
        if form.is_valid():
            form.save()
            form.add_pay(order=order)
            value = form.cleaned_data.get('value')

            messages.success(request,'Αποπληρώθηκαν %s ευρώ από το τιμολόγιο %s' %(value,order.code))
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/αποπληρωμές-τιμολογίων/')
    else:
        #checks if payment_method exists and if dont use the method of the last Deposit
        payment_method = order.payment_method

        if payment_method is None:
            payment_method = VendorDepositOrder.objects.last().payment_method
        form = PayOrderFormDeposit(initial={'payment_method':payment_method,
                                            'value':order.ipoloipo_xreostiko(), 'order':order,
                                            'day_added':timezone.now})
    context={
        'title':title,
        'form':form,
        'orders':orders,
    }
    context.update(csrf(request))
    return render(request,'inventory/pay_section/pay_orders_repayment.html',context)


def pay_order(request, dk):
    orders = Order.objects.all().filter(
         Q(status='d')|
         Q(status='p')).distinct().order_by('-day_created')
    order = Order.objects.get(id=dk)
    title =order.code
    order_pay_items= order.payorders_set.all()
    deposit_pay = order.vendordepositorderpay_set.all()


    value =order.total_price - order.credit_balance
    if request.POST:
        form = PayOrderFrom(request.POST,initial={'title':Order.objects.get(id=dk),'value':value,})
        if form.is_valid():
            form.save()
            form.update_order_and_vendor()

            messages.info(request,'Η αποπληρωμή του τιμολογίου %s ενημερώθηκε.'% title)
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/αποπληρωμές-τιμολογίων/')
    else:
       #checks if payment_method exists and if dont use the method of the last Deposit
        payment_method = order.payment_method
        if payment_method is None:
            payment_method = None
        form = PayOrderFrom(initial={'title':Order.objects.get(id=dk),'value':value,'date':timezone.now,
                                     'payment_method':payment_method,})
    context={
        'order':order,
        'form':form,
        'orders':orders,
        'pay_orders_items':order_pay_items,
        'pay_deposit':deposit_pay,
    }
    context.update(csrf(request))
    return render(request,'inventory/pay_section/pay_orders_repayment.html',context)

def orders_in_dept(request):
    orders = Order.objects.all().filter(status='d')
    title ='Υπόλοιπο Τιμολογίων'
    context={
        'title':title,
        'orders':orders,
    }
    return render(request,'inventory/pay_section/pay_orders_doseis.html', context)



def orders_in_dept_id(request,dk):
    orders = Order.objects.all().filter(status="d").order_by('-date')
    order = Order.objects.get(id=dk)
    pay_orders = PayOrders.objects.all().filter(title__code=order.code)
    title =order.code
    value =order.total_price - order.credit_balance
    if request.POST:
        form = PayOrderFrom(request.POST,initial={'title':Order.objects.get(id=dk),'value':value,})
        if form.is_valid():
            form.save()
            form.update_order_and_vendor()

            messages.info(request,'Η αποπληρωμή του τιμολογίου %s ενημερώθηκε.'% title)
            return HttpResponseRedirect('/πληρωμές/αποπληρωμές-τιμολογίων/')
    else:
        form = PayOrderFrom(initial={'title':Order.objects.get(id=dk),'value':value,})
    context={
        'order':order,
        'form':form,
        'orders':orders,
        'pay_orders':pay_orders,
    }
    context.update(csrf(request))
    return render(request,'inventory/pay_section/pay_orders_doseis_id.html',context)



def pay_orders_fullpayment(request):
    orders = Order.objects.all().filter(status="a").order_by('-day_created')
    context ={
        'orders':orders
    }
    return render(request,'inventory/pay_section/pay_orders_fullpayment.html',context)

def orders_history_id(request,dk):
    order = Order.objects.get(id=dk)
    pay_orders = PayOrders.objects.all().filter(title__code=order.code)
    title =order.code
    context={
        'title':title,
        'order':order,
        'pay_orders':pay_orders,
    }

    return render(request,'inventory/pay_section/pay_order_history.html',context)





#---------------------------------------------------------------------------------------------------------

def fixed_costs(request):
    title = 'Πάγια Έξοδα'
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')

    start_day = datetime.date.today()
    log_end_day = start_day + datetime.timedelta(days=4)
    log_expired_day = start_day - datetime.timedelta(days=100)
    ppl_end_day  = start_day + datetime.timedelta(days =5)


    log_warnings = Order_Fixed_Cost.objects.all().filter(active='a')
    log_warnings= log_warnings.filter(date__range=[str(start_day),str(log_end_day)]).order_by('date')

    log_expired = Order_Fixed_Cost.objects.all().filter(active='a')
    log_expired = log_expired.filter(date__range=[str(log_expired_day),str(start_day)]).order_by('date')


    ppl_warning = CreatePersonSalaryCost.objects.all().filter(status='a')
    ppl_expired = ppl_warning.filter(day_expire__range=[str(log_expired_day),str(start_day)]).order_by('day_expire')
    ppl_warning = ppl_warning.filter(day_expire__range=[str(start_day),str(ppl_end_day)]).order_by('day_expire')




    context = {
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'log_warnings': log_warnings,
        'log_expired':log_expired,
        "ppl_warnings":ppl_warning,
        'ppl_expired':ppl_expired,

    }
    return render(request,'inventory/pay_section/fixed_costs/homepage.html', context)



def fixed_costs_log_id(request,dk):
    # the main page for a specific bill

    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_order_log_id = Fixed_Costs_item.objects.get(id=dk)
    log = fixed_order_log_id.order_fixed_cost_set.all().filter(active='a')
    log_done = fixed_order_log_id.order_fixed_cost_set.all().filter(active='b').order_by('-date')[0:5]
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')

    title =fixed_order_log_id.title
    context ={
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'fixed_orders':fixed_order_log_id,
        'orders':log,
        'orders_done':log_done,
    }
    return render(request,'inventory/pay_section/fixed_costs/fixed_order_log_id.html', context)

def edit_log_id(request,dk,pk):
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')

    fixed_order_log_id = Fixed_Costs_item.objects.get(id=dk)
    log = fixed_order_log_id.order_fixed_cost_set.all().filter(active='a')
    log_done = fixed_order_log_id.order_fixed_cost_set.all().filter(active='b')[0:5]

    actual_log = Order_Fixed_Cost.objects.get(id=pk)
    title = 'Edit' + str(actual_log.title)

    if request.POST:
        form = LogForm(request.POST, instance=actual_log)
        if form.is_valid():
            form.save(commit=False)
            form.edit(dk=dk, pk=pk)
            form.save()
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/λογαριασμοί/%s/' %(dk))
    else:
        form =LogForm(instance=actual_log,)

    context ={
        'form':form,
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'fixed_orders':fixed_order_log_id,
        'orders':log,
        'orders_done':log_done,

    }
    context.update(csrf(request))
    return render(request, 'inventory/pay_section/fixed_costs/log_edit.html', context)









def create_new_log_cat(request):
    title = 'Δημιουργία Κατηγορίας Λογαριασμου'
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    pro = Fixed_costs.objects.get(title="Λογαριασμοί")
    if request.POST:
        form = LogFormCate(request.POST,initial={'category':pro,})
        if form.is_valid():
            form.save()
            last_item = Fixed_Costs_item.objects.last()
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/λογαριασμοί/%s/' %(last_item.id))
    else:
        form = LogFormCate(initial={'category':pro,})

    context ={
        'form':form,
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
    }
    context.update(csrf(request))
    return render(request,'inventory/pay_section/fixed_costs/add_log_category.html', context)


def create_log_order(request,dk):

    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')

    fixed_order_log_id = Fixed_Costs_item.objects.get(id=dk)
    log = fixed_order_log_id.order_fixed_cost_set.all().filter(active='a')
    log_done = fixed_order_log_id.order_fixed_cost_set.all().filter(active='b')[0:5]


    fixed_order_log_id = Fixed_Costs_item.objects.get(id=dk)
    title =fixed_order_log_id.title
    if request.POST:
        form = LogForm(request.POST,initial={'category':fixed_order_log_id})
        if form.is_valid():
            form.save()
            form.sum_up(dk=dk)
            price = form.cleaned_data.get('price')
            messages.success(request," Προστέθηκe στον λογαριασμό %s to Ποσό %s €." %(fixed_order_log_id.title, price))
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/λογαριασμοί/%s/' %(dk))
    else:
        form =LogForm(initial={'category':fixed_order_log_id,'date':timezone.now})
    context ={
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'form':form,
        'fixed_orders':fixed_order_log_id,
        'orders':log,
        'orders_done':log_done,
    }
    context.update(csrf(request))
    return render(request, 'inventory/pay_section/fixed_costs/add_log.html', context)




def pay_log_id(request,dk,pk):
    log_id = Order_Fixed_Cost.objects.get(id=pk)
    fixed_order_log_id = Fixed_Costs_item.objects.get(id=dk)
    log = fixed_order_log_id.order_fixed_cost_set.all().filter(active='a')
    log_done = fixed_order_log_id.order_fixed_cost_set.all().filter(active='b')[0:5]
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    title =fixed_order_log_id.title

    if request.POST:
        form = PayLogForm(request.POST,initial={'title':log_id.title,'date':timezone.now,'price':log_id.price, 'payment_method':log_id.payment_method})
        if form.is_valid():
            form.save()
            form.pay(dk=pk)

            messages.success(request,"H αποπληρωμή ολοκληρώθηκε")
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/λογαριασμοί/%s/' %(dk))

    else:
         form = PayLogForm(initial={'title':log_id.title,'date':timezone.now,'price':log_id.price, 'payment_method':log_id.payment_method})

    context ={
        'form':form,
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_orders':fixed_order_log_id,
        'fixed_costs_pag':fixed_costs_pag,
        'orders':log,
        'orders_done':log_done,
        'log_id':log_id,
    }
    context.update(csrf(request))
    return render(request, 'inventory/pay_section/fixed_costs/pay_log.html', context)



#--------------------people-----------------------------------------------------------------------------------------------------------------


def add_occupation(request):
    ocup_category = Fixed_costs.objects.get(title="Προσωπικό")
    title = ocup_category.title
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    if request.POST:
        form = OccupationForm(request.POST,initial={'category':ocup_category,})
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/')
    else:
        form = OccupationForm(initial={'category':ocup_category,})

    context = {
        'title':title,
        'form':form,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
    }
    return render(request, 'inventory/pay_section/fixed_costs/add_occupation.html',context)

def fixed_cost_ppl_id(request,dk):
    occup = Occupation.objects.get(id=dk)
    ppl = occup.person_set.all().filter(status='a')
    title = occup.title
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')


    context ={
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'ppl':ppl,
        'occup':occup,
    }
    return render(request,'inventory/pay_section/fixed_costs/fixed_cost_ppl_id.html', context)

def edit_ppl_id(request,dk,pk):
    occup = Occupation.objects.get(id=dk)
    ppl = occup.person_set.all().filter(status='a')
    title = occup.title
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    person = Person.objects.get(id=pk)
    title_form =person.title
    if request.POST:
        form = PersonForm(request.POST,instance=person)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/προσωπικό/%s/' %(dk))
    else:
        form = PersonForm(instance=person)


    context ={
        'form_title':title_form,
        'form':form,
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'ppl':ppl,
        'occup':occup,
    }
    context.update(csrf(request))
    return render(request,'inventory/pay_section/fixed_costs/add_person.html', context)

def pay_remaining(request,dk):

    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')

    person = Person.objects.get(id = dk)
    person_orders = person.createpersonsalarycost_set.all().filter(status ='a')
    person_hours = person.personhourscreate_set.all()
    title= person.title

    context={
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'person':person,
        'person_orders':person_orders,
        'person_hours':person_hours,


    }

    return render(request,'inventory/pay_section/fixed_costs/pay_remaining_cost_person.html', context)


def pay_remaining_id(request,dk,pk):

    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    person = Person.objects.get(id = dk)
    person_orders = person.createpersonsalarycost_set.all().filter(status = 'a')
    person_hours = person.personhourscreate_set.all()
    order_pay = CreatePersonSalaryCost.objects.get(id=pk)
    order_pay.status = 'b'
    order_pay.save()
    form_title = order_pay.title
    occup = Occupation.objects.get(title =person.occupation)
    new_pay_order = PayPersonSalaryCost.objects.create(title = order_pay.title,
                                                       person=order_pay.person,
                                                       category = order_pay.category,
                                                       payment_method = order_pay.payment_method)
    new_pay_order.save()

    person.salary_paid -= order_pay.value
    person.save()

    occup.remaining_cost +=order_pay.value
    occup.save()



    messages.success(request,'Πληρώθηκαν %s € στον Υπάλληλο %s.'%(order_pay.value,person.title))
    return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/προσωπικό/%s/' %(occup.id))

def deactivated_ppl(request,dk):
    occup = Occupation.objects.get(id=dk)
    ppl = occup.person_set.all().filter(status='a')
    title = 'Απενεργοποιημένο Προσωπικό'
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    deactived = occup.person_set.all().filter(status='b')

    context ={
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'ppl':ppl,
        'occup':occup,
        'deactivated':deactived,
    }
    return render(request, 'inventory/pay_section/fixed_costs/deactivated_ppl.html', context)

def activate_ppl(request,dk,pk):
    person = Person.objects.get(id=pk)
    person.status = 'a'
    person.save()
    return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/προσωπικό/%s/' %(dk))

def deactive(request,dk,pk):
    person = Person.objects.get(id=pk)
    person.status = 'b'
    person.save()
    return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/προσωπικό/%s/' %(dk))

def create_fixed_cost_ppl(request,dk):
    occup = Occupation.objects.get(id=dk)
    ppl = occup.person_set.all().filter(status='a')
    title = str(occup.title) + ' --- Δημιουργία'
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    if request.POST:
        form = PersonForm(request.POST,initial={'occupation':occup})
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('title')
            messages.success(request,'Ο Υπάλληλος %s δημιουργήθηκε.'%(name))
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/προσωπικό/%s/' %(dk))
    else:
        form = PersonForm(initial={'occupation':occup,'date_joined':timezone.now()})

    context = {
        'form':form,
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'ppl':ppl,
        'occup':occup,

    }
    context.update(csrf(request))
    return render(request, 'inventory/pay_section/fixed_costs/add_person.html', context)


def add_pay_order_to_person(request,dk,pk):
    occup = Occupation.objects.get(id=dk)
    person = Person.objects.get(id=pk)
    ppl = occup.person_set.all().filter(status='a')
    title = 'Προσθήκη'
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    form_title= 'Προσθήκη Πληρωμής'
    try:
        last_entry = CreatePersonSalaryCost.objects.all().filter(person=person).last()
    except:
        last_entry = None

    if request.POST:
        form = CreateFormBasicSalary(request.POST,initial={'person':person,
                                                           })
        if form.is_valid():
            form.save()
            form.add_salary(dk=dk, pk=pk)
            value = form.cleaned_data.get('value')
            messages.success(request,'Προστέθηκαν %s €  στον Υπάλληλο %s'%(value,person.title))
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/προσωπικό/%s/' %(dk))
    else:
        if last_entry:
            form= CreateFormBasicSalary(initial={'person':person,
                                            'value':last_entry.value,
                                            'category':last_entry.category,
                                            'payment_method':last_entry.payment_method,
                                            'day_expire':datetime.datetime.now()+datetime.timedelta(days=7),})
        else:
             form= CreateFormBasicSalary(initial={'person':person,})

    context = {
        'form_title':form_title,
        'form':form,
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'ppl':ppl,
        'occup':occup,

    }
    context.update(csrf(request))
    return render(request, 'inventory/pay_section/fixed_costs/add_person_pay.html', context)



def edit_people_order(request,dk, pk, ok ):
    occup = Occupation.objects.get(id=dk)
    person = Person.objects.get(id=pk)
    order_pay = CreatePersonSalaryCost.objects.get(id=ok)
    ppl = occup.person_set.all().filter(status='a')
    title = 'Επεξεργασία'
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    form_title= 'Αποθήευση Επεξεργασίας'

    if request.POST:
        form = CreateFormBasicSalary(request.POST,instance=order_pay)
        if form.is_valid():
            form.save(commit=False)
            form.edit_people_order(dk=dk, pk=pk,ok=ok)
            form.save()
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/προσωπικό/%s/' %(dk))
    else:
        form= CreateFormBasicSalary(instance=order_pay)


    context = {
        'form_title':form_title,
        'form':form,
        'title':title,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
        'ppl':ppl,
        'occup':occup

    }
    context.update(csrf(request))
    return render(request, 'inventory/pay_section/fixed_costs/add_person_pay.html', context)





#---------------------Agores/ Episkeues---------------------------------


def pagia_exoda(request,dk):
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')

    cat = Pagia_Exoda.objects.get(id=dk)
    orders = Pagia_Exoda_Order.objects.all().filter(category__title = cat.title)
    orders_done = orders.filter(active = 'b')
    orders = orders.filter(active='a')
     
    
    title = cat.title

    context = {
        'title':title,
        'cat':cat,
        'orders':orders,
        'orders_done':orders_done,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
    }
    return render(request, 'inventory/pay_section/fixed_costs/pagia_id.html', context)


def pagia_exoda_create_order(request,dk):
    cat = Pagia_Exoda.objects.get(id=dk)
    title = cat.title
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    orders = Pagia_Exoda_Order.objects.all().filter(category__title = cat.title)
    orders_done = orders.filter(active = 'b')
    orders = orders.filter(active='a')
    if request.POST:
        form = PagiaExodaOrderForm(request.POST,initial={'category':cat,})
        if form.is_valid():
            form.save()
            form.sum_up(dk=dk)
            price = form.cleaned_data.get('price')
            messages.success(request,'Στην κατηγορία %s προστέθήκαν  %s €'%(cat.title,price))
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/%s/' %(cat.id))
    else:
        form = PagiaExodaOrderForm(initial={'category':cat,'date':timezone.now})

    context = {
        'form':form,
        'title':title,
        'cat':cat,
        'orders':orders,
        'orders_done':orders_done,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
    }
    return render(request, 'inventory/pay_section/fixed_costs/pagia_id_add_order.html', context)



def pagia_exoda_create_person(request,dk):
    cat = Pagia_Exoda.objects.get(id=dk)
    title = 'Δημιουργία Εταιρίας -----' + str(cat.title)
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    orders = Pagia_Exoda_Order.objects.all().filter(category__title = cat.title)
    orders_done = orders.filter(active = 'b')
    orders = orders.filter(active='a')

    if request.POST:
        form = PersonMastorasForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/%s/' %(cat.id))
    else:
        form = PersonMastorasForm()

    context = {
        'form':form,
        'title':title,
        'cat':cat,
        'orders':orders,
        'orders_done':orders_done,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
    }
    return render(request, 'inventory/pay_section/fixed_costs/pagia_id_add_order.html', context)


def pagia_exoda_pay_order(request,dk,pk):
    cat = Pagia_Exoda.objects.get(id=dk)
    orders = Pagia_Exoda_Order.objects.all().filter(category__title = cat.title)
    orders_done = orders.filter(active = 'b')
    orders = orders.filter(active='a')
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')
    order = Pagia_Exoda_Order.objects.get(id=pk)
    
    title = order.title

    if request.POST:
        form = PagiaExodaPayOrderForm(request.POST)
        if form.is_valid():
            form.save()
            form.sums_up(dk=dk, pk=pk)
            price = form.cleaned_data.get('value')
            messages.success(request,'Πληρώσατε %s €,  στην κατηγορία %s'%(price,cat.title))
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/%s/' %(cat.id))
    else:
        form = PagiaExodaPayOrderForm(initial={'title':order.title, 'value':order.show_remain,'person':order.person,'payment_method':order.payment_method})
    
    context = {
        'form':form,
        'title':title,
        'cat':cat,
        'orders':orders,
        'orders_done':orders_done,
        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,
    }
    return render(request, 'inventory/pay_section/fixed_costs/pagia_id_add_order.html', context)
    



def pagia_exoda_edit_order(request,dk,pk):
    fixed_costs_log = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    fixed_costs_ppl = Occupation.objects.all().filter(category__title="Προσωπικό")
    fixed_costs_pag  = Pagia_Exoda.objects.all().filter(category__title ='Αγορές')

    cat = Pagia_Exoda.objects.get(id=dk)
    order = Pagia_Exoda_Order.objects.get(id=pk)
    title = order.title


    if request.POST:
        form = PagiaExodaOrderEditForm(request.POST,instance=order)
        if form.is_valid():
            form.save(commit=False)
            form.edit_order(category=cat, order=order)
            form.save()
            messages.success(request,'Η εντολή %s ενημερώθηκε.' %(order.title))
            return HttpResponseRedirect('/πληρωμές-εισπράξεις/πάγια-έξοδα/%s'%(dk))
    else:
        form = PagiaExodaOrderEditForm(instance=order)

    context ={
        'form':form,
        'title':title,
        'order':order,

        'fixed_costs_log':fixed_costs_log,
        'fixed_costs_ppl':fixed_costs_ppl,
        'fixed_costs_pag':fixed_costs_pag,


    }
    context.update(csrf(request))
    return render(request, 'inventory/pay_section/fixed_costs/pagia_id_edit.html', context)







