from django.shortcuts import render,redirect, HttpResponseRedirect , render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from PoS.models import *
from inventory_manager.form import *
from .models import Product, Supply, Category, CURRENCY, ProductPhotos, RelatedProducts, SameColorProducts
from transcations.models import *
from tools.models import ToolsTableOrder
from tools.forms import ToolsTableOrderForm
from .forms import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, Page
from django.template.context_processors import csrf
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.db.models import Sum, Avg
from account.models import CostumerAccount
from account.forms import CreateCostumerFromAdmin
from django.core.mail import send_mail,EmailMessage
from dateutil.relativedelta import relativedelta
import datetime
# Create your views here.

def update_size(id, color, post):
    all_colors = Color.objects.all()

def http_referer(request):
    return request.META.get('HTTP_REFERER')

@staff_member_required()
def welcome_page(request):
    title ="Πωλήσεις"
    today = datetime.datetime.now()
    seven_days_before = today - relativedelta(days=7)
    yesterday = today - relativedelta(days=1)
    retail_orders = RetailOrder.my_query.eshop_done_orders(date_start=seven_days_before, date_end=today)
    eshop_orders = retail_orders.filter(order_type='e')
    #last seven day orders
    last_seen_days= str('%s - %s')%(str(seven_days_before).split(' ')[0].replace('-','/'),str(today).split(' ')[0].replace('-','/'))
    retail_orders_count = retail_orders.count()
    retail_orders_incomes = retail_orders.aggregate(Sum('paid_value'))
    retail_orders_incomes = retail_orders_incomes['paid_value__sum']
    if retail_orders_incomes == None:
        retail_orders_incomes = 0
    try:
        retail_orders_avg = retail_orders_incomes/retail_orders_count
    except:
        retail_orders_avg =0

    eshop_orders_count = eshop_orders.count()
    eshop_orders_incomes = eshop_orders.aggregate(Sum('paid_value'))
    eshop_orders_incomes = eshop_orders_incomes['paid_value__sum']
    if eshop_orders_incomes == None:
        eshop_orders_incomes = 0
    try:
        eshop_orders_avg = eshop_orders_incomes/eshop_orders_count
    except:
        eshop_orders_avg =0
    #retail orders
    retail_orders_last_two_days = retail_orders.filter(day_created__range=[yesterday,today])
    retail_orders_last_two_days_date= str('%s - %s')%(str(yesterday).split(' ')[0].replace('-','/'),str(today).split(' ')[0].replace('-','/'))
    retail_last_two_days_count = retail_orders_last_two_days.count()
    retail_orders_last_two_days_incomes = retail_orders_last_two_days.aggregate(Sum('paid_value'))
    retail_orders_last_two_days_incomes = retail_orders_last_two_days_incomes['paid_value__sum']
    if retail_orders_last_two_days_incomes == None:
        retail_orders_last_two_days_incomes = 0
    try:
        retail_orders_last_two_days_avg = retail_orders_last_two_days_incomes/retail_last_two_days_count
    except:
        retail_orders_last_two_days_avg = 0
    #eshop orders
    eshop_orders_last_two_days = eshop_orders.filter(day_created__range=[yesterday,today])
    eshop_orders_two_days_count = eshop_orders_last_two_days.count()
    eshop_orders_last_two_days_incomes = eshop_orders_last_two_days.aggregate(Sum('paid_value'))
    eshop_orders_last_two_days_incomes = eshop_orders_last_two_days_incomes['paid_value__sum']
    if eshop_orders_last_two_days_incomes == None:
        eshop_orders_last_two_days_incomes = 0
    try:
        eshop_orders_last_two_days_avg = eshop_orders_last_two_days_incomes/retail_last_two_days_count
    except:
        eshop_orders_last_two_days_avg = 0
    context = {
        'title':title,
        'last_seven_days':last_seen_days,
        'retail_orders_count': retail_orders_count,
        'eshop_orders_count': eshop_orders_count,
        'retail_orders_incomes': retail_orders_incomes,
        'eshop_orders_incomes': eshop_orders_incomes,
        'retail_orders_avg': retail_orders_avg,
        'eshop_orders_avg': eshop_orders_avg,

        'retail_orders_last_two_days_date':retail_orders_last_two_days_date,
        'retail_orders_last_two_days_count':retail_last_two_days_count,
        'retail_orders_last_two_days_incomes':retail_orders_last_two_days_incomes,
        'retail_orders_last_two_days_avg':retail_orders_last_two_days_avg,

        'eshop_orders_last_two_days_count':eshop_orders_two_days_count,
        'eshop_orders_last_two_days_incomes':eshop_orders_last_two_days_incomes,
        'eshop_orders_last_two_days_avg':eshop_orders_last_two_days_avg,
        'currency':CURRENCY,

    }
    return render(request,'index.html', context)

@staff_member_required()
def welcome_page_paid_section(request):
    title = 'Πληρωμές'
    today = datetime.datetime.now()
    seven_days_before = today - relativedelta(days=7)

    #payroll

    payroll_complete = CreatePersonSalaryCost.objects.filter(status='b',day_added__range=[seven_days_before,today])
    payroll_pending = CreatePersonSalaryCost.objects.filter(status='a')

    bills_complete = Order_Fixed_Cost.objects.filter(category__category__id=1, active='b',date__range=[seven_days_before,today])
    bills_pending = Order_Fixed_Cost.objects.filter(category__category__id=1, active='a')

    check_complete = CheckOrder.objects.filter(status ='b', date_expire__range =[seven_days_before,today])
    check_pending = CheckOrder.objects.filter(status ='a')

    return render_to_response('welcome_page/index_paid.html',
                              { 'payroll_complete':payroll_complete,
                                'payroll_pending':payroll_pending,
                                'bills_complete':bills_complete,
                                'bills_pending':bills_pending,
                                'check_complete':check_complete,
                                'check_pending':check_pending,

                                    })

@staff_member_required()
def welcome_page_warehouse(request):
    today = datetime.datetime.now()
    last_month = today - relativedelta(days=30)
    vendors = Supply.objects.all().order_by('-balance')[0:10]
    products = OrderItem.objects.all()[0:15]
    orders_complete = Order.objects.filter(status='a', day_created__range=[last_month,today])[0:10]
    orders_pending = Order.objects.filter(status__in =['p', 'd'])

    return render_to_response('welcome_page/welcome_warehouse.html',{
                             'orders_complete':orders_complete,
                             'orders_pending':orders_pending,
                             'vendors':vendors,
                             'products':products,
     })

@staff_member_required()
def vendors(request):
    #vendors page
    title='Προμηθευτές'
    table_order = ToolsTableOrder.objects.get(title='warehouse_table_vendor_order')
    vendor = Supply.objects.all()
    if request.POST:
        query = request.POST.get('search_pro')
        if query:
            vendor = vendor.filter(
                Q(title__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query) |
                Q(phone1__icontains=query) |
                Q(fax__icontains=query)
            ).distinct()
    if 'table_form' in request.POST:
        form = ToolsTableOrderForm(request.POST, instance=table_order)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = ToolsTableOrderForm(instance=table_order)

    try:
        if table_order.table_order_by == 'edit':
            pass
        else:
            vendor = vendor.order_by('%s'%(table_order.table_order_by))
    except:
        pass
    paginator = Paginator(vendor,table_order.show_number_of_products)
    page = request.GET.get('page')
    try:
        contracts= paginator.page(page)
    except PageNotAnInteger:
        contracts= paginator.page(1)
    except EmptyPage:
        contracts = paginator.page(paginator.num_pages)
    context = {
        'vendors': contracts,
        'title': title,
        'form': form,
        'contacts': contracts,
    }
    return render(request, 'inventory/vendors_edit_section_NEW.html',context)

@staff_member_required()
def ajax_vendors(request):
    if request.POST:
        search_text = request.POST['search_text']
    else:
        search_text = ''
    if len(search_text) <= 2:
        return render_to_response('ajax/ware_product_search.html',{'my_vendors':None,})
    else:
        vendors=Supply.objects.filter(title__contains=search_text)
        return render_to_response('ajax/ware_product_search.html',{'my_vendors':vendors,})

@staff_member_required()
def create_vendor(request):
    title = 'Δημιουργία Προμηθευτή'
    if request.POST:
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('title')
            messages.success(request,'O Προμηθευτής %s δημιουργήθηκε.' %(name))
            return HttpResponseRedirect('/αποθήκη/προμηθευτές/')
        form_Doy = TaxesForm(request.POST)
        if form_Doy.is_valid():
            form_Doy.save()
            name = form_Doy.cleaned_data.get('title')
            messages.success(request,'O Προμηθευτής %s δημιουργήθηκε.' %(name))
            return HttpResponseRedirect('/αποθήκη/προμηθευτές/δημιουργία/')

    else:
        form = VendorForm()
        form_Doy = TaxesForm()

    context = {
        'title':title,
        'form':form,
        'form_taxes':form_Doy,
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_vendor.html' ,context)

@staff_member_required()
def edit_vendor(request,dk):
    vendor = Supply.objects.get(id= dk)
    title = 'Επεξεργασία %s'%(vendor.title)
    if request.POST:
        form = VendorForm(request.POST,instance=vendor)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('title')
            messages.success(request,'O Προμηθευτής %s επεξεργάστηκε.' %(name))
            return HttpResponseRedirect('/αποθήκη/προμηθευτές/')
        form_Doy = TaxesForm(request.POST)
        if form_Doy.is_valid():
            form_Doy.save()
            name = form_Doy.cleaned_data.get('title')
            messages.success(request,'H ΔοΥ %s δημιουργήθηκε.' %(name))
            return HttpResponseRedirect('/αποθήκη/προμηθευτές/επεξεργασία/%s/'%(dk))

    else:
        form = VendorForm(instance=vendor)
        form_Doy = TaxesForm()

    context = {
        'title':title,
        'form':form,
        'form_taxes':form_Doy,
        'vendor':vendor,
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_vendor.html' ,context)

@staff_member_required()
def vendor_check_order(request, dk):
    # adds a new check payment to vendor with date expire
    title = 'Προσθήκη Επιταγής'
    vendor = Supply.objects.get(id=dk)
    vendors = Supply.objects.all()
    if request.POST:
        form = CheckOrderForm(request.POST,initial={'debtor':vendor})
        if form.is_valid():
            form.save()
            form.create_vendor_deposit_order()
            value = form.cleaned_data.get('value')
            messages.success(request, 'Προστέθηκαν %s  ευρώ στον Προμηθευτή %s ' %(value,vendor.title))
            return HttpResponseRedirect('/αποθήκη/προμηθευτές/')
    else:
        form = CheckOrderForm(initial={'debtor':vendor,'date_expire':timezone.now()})

    context ={
        'title':title,
        'vendors':vendors,
        'form':form,
        'vendor':vendor,
    }
    context.update(csrf(request))
    return render(request, 'inventory/vendor_add_deposit.html', context)

@staff_member_required()
def vendor_deposit_order(request,dk):
    #adds a new deposit to the vendor
    title = 'Προσθήκη Προκαταβολής'
    vendor = Supply.objects.get(id=dk)
    vendors = Supply.objects.all()
    if request.POST:
        form = DepositVendorForm(request.POST,initial={'vendor':vendor})
        if form.is_valid():
            form.save()
            form.refresh(dk=dk)
            value = form.cleaned_data.get('value')
            messages.success(request, 'Προστέθηκαν %s  ευρώ στον Προμηθευτή %s ' %(value,vendor.title))
            return HttpResponseRedirect('/αποθήκη/προμηθευτές/')
    else:
        form = DepositVendorForm(initial={'vendor':vendor})

    context ={
        'title':title,
        'vendors':vendors,
        'form':form,
        'vendor':vendor,
    }
    context.update(csrf(request))
    return render(request, 'inventory/vendor_add_deposit.html', context)

@staff_member_required()
def check_orders_management(request):
    all_check_orders = CheckOrder.objects.all()
    vendors = Supply.objects.all()
    payment_method = PaymentMethod.objects.all()
    try:
        vendor_name = request.session['check_ven_fi']
    except:
        request.session['check_ven_fi'] = ''
        vendor_name =None
    payment_name = None
    date_pick = None
    if request.GET:
        all_check_orders = CheckOrder.objects.all()
        vendor_name = request.GET.getlist('vendor_name')
        payment_name = request.GET.getlist('payment_name')
        date_pick = request.GET.get('date_pick')
        if vendor_name:
            request.session['check_ven_fi']=vendor_name
            all_check_orders = all_check_orders.filter(debtor__title__in= vendor_name)
            #checks_done = checks_done.filter(debtor__title__in=vendor_name)
        if payment_name:
            all_check_orders = all_check_orders.filter(place__title__in=payment_name)
            #checks_done = checks_done.filter(place__title__in=payment_name)
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            all_check_orders = all_check_orders.filter(date_expire__range=[date_start,date_end])
        except:
            date_pick = None
    total = all_check_orders.aggregate(Sum('value'))
    total = total['value__sum']
    if not total:
        total = 0
    orders_done = all_check_orders.filter(status ='b').aggregate(Sum('value'))
    orders_done = orders_done['value__sum']
    if not orders_done:
        orders_done = 0
    orders_in_progress = all_check_orders.filter(status ='a').aggregate(Sum('value'))
    orders_in_progress = orders_in_progress['value__sum']
    if not orders_in_progress:
        orders_in_progress =0
    payment_analysis = {}
    for order in all_check_orders:
        try:
            payment_analysis[order.place.title] += order.value
        except:
            payment_analysis[order.place.title] = order.value



    title = 'Διαχείρηση επιταγών'
    page = request.GET.get('page', 1)
    paginator = Paginator(all_check_orders, 10)
    try:
        orders_paginate = paginator.page(page)
    except PageNotAnInteger:
        orders_paginate = paginator.page(1)
    except EmptyPage:
        orders_paginate = paginator.page(paginator.num_pages)
    context = locals()
    return render(request, 'inventory/check_orders_managment.html', context)

@staff_member_required()
def payment_check(request, dk):
    check_order = CheckOrder.objects.get(id = dk)
    check_order.status = 'b'
    check_order.save()
    return HttpResponseRedirect('/αποθήκη/προμηθευτές/διαχείρηση-επιταγών/')

@staff_member_required()
def edit_check_order(request,dk):
    check = CheckOrder.objects.get(id=dk)
    check_value = check.value
    check_debtor =  check.debtor
    check_place = check.place
    checks = CheckOrder.objects.all().order_by('-date_expire').filter(status ='a')
    checks_done = CheckOrder.objects.all().order_by('-date_expire').exclude(status ='a')
    title = 'Διαχείρηση %s, %s ' %(check.debtor.title, check.place.title)
    if request.POST:
        form = CheckOrderForm(request.POST, instance=check)
        if form.is_valid():
            check_debtor.remaining_deposit -= check_value
            check_debtor.save()
            check_place.balance -= check_value
            check_place.save()
            check_debtor.remaining_deposit += form.cleaned_data.get('value')
            check_debtor.save()
            new_place = form.cleaned_data.get('place')
            new_place.balance += form.cleaned_data.get('value')
            new_place.save()
            form.save()
            return HttpResponseRedirect('/αποθήκη/προμηθευτές/διαχείρηση-επιταγών/')
    else:
        form = CheckOrderForm(instance=check)

    context = {
        'title':title,
        'checks':checks,
        'form':form,
        'checks_done':checks_done,

    }
    context.update(csrf(request))

    return render(request, 'inventory/edit_check_orders.html', context)

#---------------------------------Costumers---------------------------------------

def costumers_section(request):
    costumers = CostumerAccount.objects.all()
    costumers_details = {}
    taxes_city = TaxesCity.objects.all()
    if request.POST:
        print(request.POST)
    form = CostumerForm()
    currency = CURRENCY
    context= locals()
    return render(request, 'inventory/costumers_section.html', context)


def costumers_new(request):
    if request.POST:
        form = CreateCostumerFromAdmin(request.POST)
        if form.is_valid():
            user =form.save(commit=False)
            password = 'asopos10'
            user.set_password(password)
            user.save()
            new_user_account = CostumerAccount.objects.create(user=user,
                                                              shipping_address_1=form.cleaned_data.get('address'),
                                                              shipping_city = form.cleaned_data.get('city'),
                                                              shipping_zip_code = form.cleaned_data.get('zip_code'),
                                                              cellphone = form.cleaned_data.get('cell'),
                                                              phone = form.cleaned_data.get('phone'),
                                                              phone1 = form.cleaned_data.get('phone1'),
                                                              billing_name = form.cleaned_data.get('username'),
                                                              billing_address = form.cleaned_data.get('address'),
                                                              billing_city = form.cleaned_data.get('city'),
                                                              billing_zip_code = form.cleaned_data.get('zip_code'),

                                                              )
            new_user_account.save()
            return HttpResponseRedirect('/αποθήκη/costumers/')
    else:
        form = CreateCostumerFromAdmin()
    title = 'Δημιουργία Πελάτη'
    return_page='/αποθήκη/costumers/'
    context = {
        'title':title,
        'return_page':return_page,
        'form':form,
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html',context)

def edit_costumer(request,dk):
    costumer = CostumerAccount.objects.get(id=dk)
    if request.POST:
        form = CreateCostumerFromAdmin(request.POST, instance=costumer)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/costumers/')
    else:
        form =CreateCostumerFromAdmin(instance=costumer)
    title='Επεξεργασία Πελάτη'
    context = {
        'form':form,
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html', context)


#------------------------Παραγγελίες---------------------------------
from django.core.mail import EmailMultiAlternatives


def pre_order_section(request):
    pre_order = PreOrder.objects.all()
    #pre_orders statement
    pre_order_statement = PreOrderStatement.objects.all().order_by('-id').filter(consume_to_order=False)
    paginator = Paginator(pre_order_statement, 15) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        pre_order_statement = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pre_order_statement = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pre_order_statement = paginator.page(paginator.num_pages)
    pre_order_statement_done_to_order = PreOrderStatement.objects.all().filter(consume_to_order=True)
    #-----------------------------------------------------------------------------
    pre_order_active = PreOrder.objects.filter(status='a').last()
    items_pre_order_active = PreOrderItem.objects.filter(order = pre_order_active).order_by('title__supplier')
    new_items_pre_order_active = PreOrderNewItem.objects.filter(order = pre_order_active).order_by('vendor__title')
    vendors = []
    for item in items_pre_order_active:
        if item.title.supplier in vendors:
            continue
        else:
             vendors.append(item.title.supplier)
    for item in new_items_pre_order_active:
        if item.vendor in vendors:
            continue
        else:
            vendors.append(item.vendor)
    vendor_sum =[]
    for vendor in vendors:
        vendor_suma = 0
        total_sum = items_pre_order_active.filter(title__supplier=vendor)
        total_new_sum = new_items_pre_order_active.filter(vendor=vendor)
        for item in total_sum:
            vendor_suma += item.qty*item.title.price_buy
        for item in total_new_sum:
            vendor_suma += item.price_buy*item.qty
        vendor_sum.append((vendor,vendor_suma))
    if request.POST:
        email_list = request.POST.getlist('email_list')
        print_list = request.POST.getlist('print_list')
        try:
            last_order  = PreOrderStatement.objects.last().id
            title = 'ΑΡ.'+ str(int(last_order)+1)+ ', '+ str(vendor.title)
        except:
            title = 'ΑΡ.1'+ ', '+str(vendor.title)
        for vendor in vendors:
            sented = 'a'
            printed = 'a'
            if str(vendor.id) in email_list:
                sented ='b'
            if str(vendor.id) in print_list:
                printed='b'
            new_order = PreOrderStatement.objects.create(title=title,
                                                            vendor=vendor,
                                                            send_status = sented,
                                                            print_status=printed,
                                                            )
            new_order.save()
            messages.success(request,'Προπαραγγελία δημιουργήθηκε.')
            for item in items_pre_order_active:
                if item.title.supplier == vendor:
                    new_item = PreOrderStatementItem.objects.create(title=item.title,
                                                                    order =PreOrderStatement.objects.last(),
                                                                    qty=item.qty)
                    new_item.save()
            for item in new_items_pre_order_active:
                if item.vendor == vendor:
                    print(item.title, item.qty)
                    new_item_again =  PreOrderStatementNewItem.objects.create(title=item.title,
                                                                              order = PreOrderStatement.objects.last(),
                                                                              vendor = item.vendor,
                                                                    qty = item.qty,
                                                                    price_buy = item.price_buy,
                                                                    #discount_buy = item.discount_buy,
                                                                    #price = item.price,


                                                                    )
                    new_item_again.save()
                    if item.sku:
                        new_item_again.sku = item.sku
                    if item.category:
                        new_item_again.category = item.category
                    if item.brand:
                        new_item_again.brand = item.brand
                    if item.size:
                        new_item_again.size = item.size
                    if item.color:
                        new_item_again.color = item.color
                    new_item_again.save()
            if sented =='b':
                content="<h1>Επαναλαμβόμενα Προϊόντα</h1><br>"
                items = new_order.preorderstatementitem_set.all()
                new_items = new_order.preorderstatementnewitem_set.all()
                for ele in items:
                    content += '%s - %s <br>'%(ele.title.title,ele.qty)

                content += "<h1>Νέα Προϊόντα </h1>"

                for ele in new_items:
                    content += '%s - %s <br>'%(ele.title,ele.qty)
                subject, from_email, to = 'hello', 'christosstath10@gmail.com', '%s'%(new_order.vendor.email)
                text_content = 'Νέα Παραγγελία - Γρηγόρης ΣταΘάκης'
                html_content = '<p>%s</p>'%(content)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
        pre_order_active.status = 'b'
        pre_order_active.save()
        return HttpResponseRedirect('/αποθήκη/pre-order-section/')
    context = {
        'pre_order':pre_order,
        'pre_order_active':pre_order_active,
        'pre_order_statement':pre_order_statement,
        'pre_order_items':items_pre_order_active,
        'pre_order_new_items':new_items_pre_order_active,
        'vendors':vendor_sum,

    }
    context.update(csrf(request))
    return render(request, 'inventory/pre_order_section.html', context)


def pre_order_edit_item(request,dk):
    order_item = PreOrderItem.objects.get(id=dk)
    if request.POST:
        form = PreOrderItemForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/pre-order-section/')
    else:
         form = PreOrderItemForm(instance=order_item)
    context ={
        'form':form,
        'title':'Επεξεργασία %s'%(order_item.title.title),
        'return_page':'/αποθήκη/pre-order-section/',
    }
    context.update(request)
    return render(request, 'inventory/create_costumer_form.html', context)


def pre_order_delete_item(request, dk):
    pre_order_item = PreOrderItem.objects.get(id=dk)
    pre_order_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def pre_order_create(request):
    if request.POST:
        form = PreOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/pre-order-section/')
    else:
        form = PreOrderForm()
    context = {
        'form':form,
        'return_page':'/αποθήκη/pre-order-section/',
        'title':'Δημιοργία Φόρμας Παραγγελίας',

    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)


def pre_order_create_new_item(request):
    if request.POST:
        form = PreOrderNewItemForm(request.POST, initial={'order':PreOrder.objects.filter(status='a').last()})
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/pre-order-section/')
    else:
        form = PreOrderNewItemForm( initial={'order':PreOrder.objects.filter(status='a').last()})

    context = {
        'title':'ΠροΠαραγγελία.. Δημιουργία Προϊόντος',
        'form':form,
        'return_page':'/αποθήκη/pre-order-section/',
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

def pre_order_delete_new_item(request, dk):
    order_item = PreOrderNewItem.objects.get(id=dk)
    order_item.delete()
    return HttpResponseRedirect('/αποθήκη/pre-order-section/')

def pre_order_edit_new_item(request,dk):
    if request.POST:
        form = PreOrderNewItemForm(request.POST, instance=PreOrderNewItem.objects.get(id=dk))
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/pre-order-section/')
    else:
        form = PreOrderNewItemForm(instance=PreOrderNewItem.objects.get(id=dk))

    context = {
            'title':'ΠροΠαραγγελία.. Δημιουργία Προϊόντος',
            'form':form,
            'return_page':'/αποθήκη/pre-order-section/',
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)


def pre_order_show_statement(request, dk):
    pre_order_statement = PreOrderStatement.objects.get(id=dk)
    pre_order_items = pre_order_statement.preorderstatementitem_set.all()
    pre_order_new_items = pre_order_statement.preorderstatementnewitem_set.all()
    context = {
        'order':pre_order_statement,
        'order_items':pre_order_items,
        'new_order_items':pre_order_new_items,
        }
    return render(request, 'inventory/pre_order_section.html', context)

def pre_order_show_statement_edit_product(request,dk,pk):
    pre_order_statement = PreOrderStatement.objects.get(id=dk)
    pre_order_statement_product = PreOrderStatementItem.objects.get(id=pk)
    if request.POST:
        form = PreOrderStatementItemForm(request.POST, instance=pre_order_statement_product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/pre-order-section/order-statement/%s'%(dk))
    else:
        form = PreOrderStatementItemForm(instance=pre_order_statement_product)
    context = {
        'form': form,
        'title': 'Επεξεργασία %s'%(pre_order_statement.title),
        'return_page': '/αποθήκη/pre-order-section/order-statement/%s'%(dk),
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

def pre_order_show_statement_edit_new_product(request,dk,pk):
    pre_order_statement = PreOrderStatement.objects.get(id=dk)
    pre_order_statement_new_product = PreOrderStatementNewItem.objects.get(id=pk)
    if request.POST:
        form = PreOrderStatementNewItemForm(request.POST, instance=pre_order_statement_new_product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/pre-order-section/order-statement/%s'%(dk))
    else:
        form = PreOrderStatementNewItemForm(instance=pre_order_statement_new_product)
    context = {
        'form':form,
        'title':'Επεξεργασία %s'%(pre_order_statement.title),
        'return_page':'/αποθήκη/pre-order-section/order-statement/%s'%(dk),
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)


def create_order_from_pre_order_statement(request, dk):
    date_now = datetime.datetime.today()
    pre_order_statement = PreOrderStatement.objects.get(id=dk)
    pre_order_statement_items = pre_order_statement.preorderstatementitem_set.all()
    pre_order_statement_new_items = pre_order_statement.preorderstatementnewitem_set.all()



    if request.POST:
        form = OrderForm(request.POST, initial={'vendor':pre_order_statement.vendor,
                                                'date':date_now,})
        if form.is_valid():
            form.save()

            current_order = Order.objects.last()
            for product in pre_order_statement_new_items:
                product_create = Product.objects.create(title=product.title,
                                                        supplier=product.vendor,
                                                        price_buy=product.price_buy or 0,
                                                        ekptosi = product.discount_buy or 0,
                                                        category = product.category,
                                                        price = product.price or 0)

                product_create.save()
                order_item_create = OrderItem.objects.create(product = product_create,
                                                             order= current_order,
                                                             unit =Unit.objects.get(name='Τεμάχ'),
                                                             discount =product_create.ekptosi,
                                                             taxes = 'c',
                                                             qty = product.qty,
                                                             price = product_create.price_buy,
                                                             )

                order_item_create.save()
                order_item_create.pre_order_add_to_product(product=product_create, qty=product.qty)
                order_item_create.pre_order_add_to_order(order=current_order, qty=product.qty)




            for product in pre_order_statement_items:
                order_item_create = OrderItem.objects.create(product = product.title,
                                                             order= current_order,
                                                             unit =Unit.objects.get(name='Τεμάχ'),
                                                             discount =product.title.order_discount,
                                                             taxes = 'c',
                                                             qty = product.qty,
                                                             price = product.title.price_buy,
                                                             )

                order_item_create.save()
                order_item_create.pre_order_add_to_product(product=product.title, qty=product.qty)
                order_item_create.pre_order_add_to_order(order=current_order, qty=product.qty)
            pre_order_statement.consume_to_order = True
            pre_order_statement.save()
            messages.success(request,'Τα τιμολόγια δημιουργήθηκαν.')
            return HttpResponseRedirect('/αποθήκη/τιμολόγια/επεξεργασία/%s/'%(current_order.id))
    else:
        form = OrderForm(initial={'vendor':pre_order_statement.vendor,
                                                'date':date_now,})

    context={
        'form':form,
        'title':'Δημιουργία Τιμολογίου από %s' %(pre_order_statement.title),
        'return_page':'/αποθήκη/pre-order-section/',
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)


'''
def add_product_to_pre_order(request, dk):
    active_order = PreOrder.objects.filter(active=True).last()
    if not active_order:
        redirect('pre_order_section')
    get_product = Product.objects.get(id=dk)
    if request.POST:
'''