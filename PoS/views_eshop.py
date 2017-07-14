from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import *
from .forms import *
from django.template.context_processors import csrf
from django.db.models import Q
from django.contrib import messages
from django.db.models import Avg, Sum
from products.forms import CostumerEshopForm
from account.forms import CostumerAccount, RegisterFormFromAdmin, CreateCostumerPosForm
from account.models import CostumerAccount
from django.contrib.auth.models import User
from .tools import *



@staff_member_required
def eshop_homepage(request):
    orders = RetailOrder.objects.all().filter(order_type='e')
    context = locals()
    return render(request,'PoS/eshop/homepage.html',context)

@staff_member_required
def eshop_new_order(request):
    costumers = CostumerAccount.objects.all()
    payment_methods = PaymentMethod.objects.all()
    brands = Brands.objects.all()
    main_categories = CategorySite.objects.all().filter(category=None)
    products = Product.my_query.active_warehouse()
    request.session['new_order'] = 0
    shipping = Shipping.objects.all().filter(active='a')
    try:
        get_cart_items = request.session['cart_items']
        cart_items=[]
        for item in get_cart_items:
            product = Product.objects.get(id=item[0])
            cart_items.append((product,1))
            request.session['new_order'] +=float(product.price_internet)
    except:
        cart_items = None
    if 'submit_order' in request.POST:
        request.session['form_costumer']= request.POST.get('costumer_name')
        request.session['form_payment_method'] = request.POST.get('payment_name')
        request.session['form_shipping'] = request.POST.get('shipping_name')
        return HttpResponseRedirect('/PoS/eshop/new-order/submit/')
        #print(request.session['form_costumer'],request.session['form_payment_method'],request.session['form_shipping'])
    if 'search_fil' in request.POST:
        brand_name = request.POST.getlist('brand_name')
        category_name = request.POST.getlist('main_cat')
        if brand_name:
            products = products.filter(brand__id__in=brand_name)
        if category_name:
            products = products.filter(category__id__in=category_name)

    if 'new_costumer' in  request.POST:
        form_new_costumer = RegisterFormFromAdmin(request.POST)
        if form_new_costumer.is_valid():
            #form_new_costumer.clean_email2()
            #form_new_costumer.clean_password2()
            user =form_new_costumer.save(commit=False)
            password = form_new_costumer.cleaned_data.get('password')
            user.set_password(password)
            user.save()

            new_user_account = CostumerAccount.objects.create(user=user,
                                                              shipping_address_1=form_new_costumer.cleaned_data.get('address'),
                                                              shipping_city = form_new_costumer.cleaned_data.get('city'),
                                                              shipping_zip_code = form_new_costumer.cleaned_data.get('zip_code'),
                                                              cellphone = form_new_costumer.cleaned_data.get('cell'),
                                                              phone = form_new_costumer.cleaned_data.get('phone'),
                                                              phone1 = form_new_costumer.cleaned_data.get('phone1'),
                                                              billing_name = form_new_costumer.cleaned_data.get('username'),
                                                              billing_address = form_new_costumer.cleaned_data.get('address'),
                                                              billing_city = form_new_costumer.cleaned_data.get('city'),
                                                              billing_zip_code = form_new_costumer.cleaned_data.get('zip_code'),

                                                              )
            new_user_account.save()
            request.session['current_costumer_account'] = CostumerAccount.objects.get(user=user).id

            return HttpResponseRedirect('/PoS/eshop/new-order/')
    else:
        form_new_costumer=RegisterFormFromAdmin()

    try:
        costumer_current_id = request.session['current_costumer_account']
        costumer_current_id = CostumerAccount.objects.get(id=costumer_current_id)
    except:
        costumer_current_id =None
    context={
        'products':products,
        'costumers':costumers,
        'brands':brands,
        'categories':main_categories,
        'cart_items':cart_items,
        'payment_method':payment_methods,
        'shipping':shipping,
        'form_new_costumer':form_new_costumer,
        'current_costumer':costumer_current_id,

    }
    context.update(csrf(request))
    return render(request,'PoS/eshop/eshop_order_section.html', context)

def eshop_add_costumer_account(request,dk):
    request.session['current_costumer_account'] = dk
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def eshop_add_product(request,dk):
    product = Product.objects.get(id=dk)
    try:
        sessionlist = request.session['cart_items']
        sessionlist.append((product.id,1))
        request.session['cart_items'] = sessionlist
    except:
        sessionlist = []
        sessionlist.append((product.id,1))
        request.session['cart_items'] = sessionlist


    #request.session['cart_items'] = None
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def eshop_delete_product(request,dk):
    product = Product.objects.get(id=dk)
    session_list = request.session['cart_items']
    session_list.remove([product.id,1])
    request.session['cart_items'] =session_list

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_eshop_order(request):
    try:
        costumer = request.session['current_costumer_account']
        costumer = CostumerAccount.objects.get(id=costumer)
    except:
        messages.warning(request,"Δεν έχετε επιλέξει Πελάτη")


    try:
        payment_name = PaymentMethod.objects.get(title=request.session['form_payment_method'])
    except:
        messages.warning(request,"Δεν έχετε επιλέξει Τρόπο ΠΛηρωμής")

    try:
        shipping_name = Shipping.objects.get(title=request.session['form_shipping'])
    except:
        messages.warning(request,"Δεν έχετε επιλέξει Τρόπο Αποστολής")

    cart_items=[]
    try:
        get_cart_items = request.session['cart_items']

        for item in get_cart_items:
            product = Product.objects.get(id=item[0])
            cart_items.append((product,1))
            request.session['new_order'] +=float(product.price_internet)


    except:
        messages.warning(request,'Επιλέξτε')

    try:
        new_order = Lianiki_Order.objects.create(costumer_account=costumer,
                                                 payment_method=payment_name,
                                                 shipping=shipping_name,
                                                 title='hello',
                                                 status = Order_status.objects.get(id=1),
                                                 order_type= TypeOfOrder.objects.get(title='Eshop')
                                                 )
        new_order.save()
        lianiki_order = Lianiki_Order.objects.last()
        for item in cart_items:
            product = item[0]
            new_order_item = LianikiOrderItem.objects.create(title=product,
                                                             order= lianiki_order,
                                                             cost=product.price_buy,
                                                             price =product.price_internet,
                                                             qty=1)
            new_order_item.save()
            new_order_item.add_item_auto(order=lianiki_order,product=product)



        request.session['form_costumer']= None
        request.session['form_payment_method'] = None
        request.session['form_shipping'] = None
        request.session['cart_items'] = None
        request.session['new_order'] = 0
        request.session['current_costumer_account']=None
        print('all_ok!')



    except:
        print('Something its fucked!')


    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def orders_management(request):
    orders = RetailOrder.my_query.eshop_orders()
    orders_a = orders.exclude(status_id=7)
    orders_items = RetailOrderItem.objects.filter(order__in=orders_a)
    order_items_found = orders_items.filter(is_find=True)
    order_items_not_found = orders_items.filter(is_find=False)
    order_status = Order_status.objects.all()
    new_orders = orders.filter(status__id=1)
    order_in_progress = orders.filter(status__id=2)
    orders_ready_to_go = orders.filter(status__id=5)
    orders_sent = orders.filter(status__id=6)
    orders_get_paid = orders.filter(status_id=7)
    orders_in_waiting = orders.filter(status__id__in=[3,4])
    context = {
        'new_orders':new_orders,
        'status':order_status,
        'orders_in_progress':order_in_progress,
        'orders_ready_to_go':orders_ready_to_go,
        'orders_sent':orders_sent,
        'orders_in_waiting':orders_in_waiting,
        'order_items':orders_items,
        'order_items_found':order_items_found,
        'order_items_not_found':order_items_not_found,
        'order_get_paid':orders_get_paid,

    }
    return render(request,'PoS/eshop/eshop_order_management.html', context)

def orders_management_details(request,dk):
    orders = Lianiki_Order.objects.all().filter(order_type__title='Eshop')
    orders_a = orders.exclude(status_id =7)


    order_status = Order_status.objects.all()
    new_orders = orders.filter(status__id=1)
    order_in_progress = orders.filter(status__id=2)
    orders_ready_to_go = orders.filter(status__id=5)
    orders_sent = orders.filter(status__id=6)
    orders_get_paid = orders.filter(status_id=7)

    orders_in_waiting = orders.filter(status__id__in=[3,4])




    order = Lianiki_Order.objects.get(id=dk)
    orders_items = LianikiOrderItem.objects.all().filter(order=order)
    order_items_found = orders_items.filter(is_find=True)
    order_items_not_found = orders_items.filter(is_find=False)



    context ={
        'new_orders':new_orders,
        'status':order_status,
        'orders_in_progress':order_in_progress,
        'orders_ready_to_go':orders_ready_to_go,
        'orders_sent':orders_sent,
        'orders_in_waiting':orders_in_waiting,
        'order_items':orders_items,
        'order_items_found':order_items_found,
        'order_items_not_found':order_items_not_found,
        'order_get_paid':orders_get_paid,

    }
    return render(request,'PoS/eshop/eshop_order_management.html', context)

def orders_management_change(request,dk,pk):
    order = Lianiki_Order.objects.get(id=dk)
    new_status = Order_status.objects.get(id=pk)
    order.status=new_status
    order.save()
    if int(pk) == 5:
        order_items = order.lianikiorderitem_set.all()
        for item in order_items:
            item.is_find =True
            item.save()
    if int(pk) == 6:
        order_items = order.lianikiorderitem_set.all()
        for item in order_items:
            item.is_find =True
            item.save()
    if int(pk) == 7:
        order_items = order.lianikiorderitem_set.all()
        for item in order_items:
            item.is_find =True
            item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def orders_management_product_change(request,dk):
    item= LianikiOrderItem.objects.get(id=dk)
    if item.is_find:
        item.is_find=False
        item.save()
        order = item.order
        order.status =Order_status.objects.get(id=2)
        order.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        item.is_find =True
        item.save()
        order = item.order
        order.status = Order_status.objects.get(id=2)
        order.save()
        order_items = order.lianikiorderitem_set.all()
        for ele in order_items:
            if ele.is_find:
                continue
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.status = Order_status.objects.get(id=5)
        order.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

