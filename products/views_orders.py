from django.shortcuts import render,redirect, HttpResponseRedirect , render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from inventory_manager.form import *
from .models import Product, Supply, Category, CURRENCY, ProductPhotos, RelatedProducts, SameColorProducts
from transcations.models import *
from tools.models import ToolsTableOrder
from tools.forms import ToolsTableOrderForm
from .forms import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, Page
from django.template.context_processors import csrf

from django.contrib import messages
from django.db.models import Q



#------------------------------order_section-------------------------------------------------------------------------

@staff_member_required()
def orders(request):
    #order main page
    vendors = Supply.objects.all()
    last_order = Order.objects.last()
    title = 'Τιμολόγια'
    table_order = ToolsTableOrder.objects.get(title='warehouse_table_order_order')
    order = Order.objects.all().filter(status='p').order_by('-date')
    #filters
    try:
        vendor_name = request.session['ware_order_ven']
    except:
        vendor_name=''
        request.session['ware_order_ven']=''
    if request.POST:
        query = request.POST.get('search_pro')
        if query:
            order = order.filter(
                Q(day_created__icontains=query) |
                Q(code__icontains=query) |
                Q(vendor__title__contains=query)

            ).distinct()
    if 'table_form' in request.POST:
        form =ToolsTableOrderForm(request.POST, instance=table_order)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = ToolsTableOrderForm(instance=table_order)
    if 'ven' in request.POST:
        vendor_name = request.POST.getlist('vendor_name')
        if vendor_name:
            order = order.filter(vendor__title__in=vendor_name)
            request.session['ware_order_ven'] = vendor_name
        else:
            request.session['ware_order_ven']=None
    order = order.order_by('%s'%(table_order.table_order_by))
    paginator = Paginator(order,table_order.show_number_of_products)
    page = request.GET.get('page')
    try:
        order = paginator.page(page)
    except PageNotAnInteger:
        order = paginator.page(1)
    except EmptyPage:
        order = paginator.page(paginator.num_pages)
    context = {
        'last_order':last_order,
        'orders':order,
        'contacts':order,
        'title':title,
        'vendors':vendors,
        'tools_table':table_order,
        'form':form,
    }
    return render(request, 'inventory/orders_edit_section_NEW.html',context)

@staff_member_required()
def ajax_orders(request):
    if request.POST:
        search_text = request.POST['search_text']
    else:
        search_text = ''
    if len(search_text) <= 2:
        return render_to_response('ajax/ware_product_search.html',{'my_orders':None,})
    else:
        vendors = Order.objects.filter(
            Q(notes__contains=search_text) |
            Q(vendor__title__contains=search_text) |
            Q(code__contains=search_text)
            ).distinct()
        print(vendors)
        return render_to_response('ajax/ware_product_search.html',{'my_orders':vendors,})

@staff_member_required()
def create_order(request):
    #creates a new order
    title = 'Δημιουργία τιμολογίου'
    last_order = Order.objects.all().filter(status='p').last()

    if request.POST:
        form = OrderForm(request.POST,)
        if form.is_valid():
            form.save()
            updated_order = Order.objects.last()
            updated_order.taxes_modifier = updated_order.vendor.taxes_modifier
            updated_order.save()
            return HttpResponseRedirect('/αποθήκη/τιμολόγια/επεξεργασία/%s' %(updated_order.id))

    else:
        form = OrderForm(initial={'date':timezone.now})


    context = {
        'title':title,
        'form':form,
        'last_order':last_order,
    }
    context.update(csrf(request))
    return render(request,'inventory/new_all_NEW.html',context)

@staff_member_required()
def delete_order(request, dk):
    order = Order.objects.get(id=dk)
    order_items = order.orderitem_set.all()
    pay_orders = order.payorders_set.all()
    for pay_order in pay_orders:
        pay_order.delete_pay()
        pay_order.delete()
    pay_orders_deposit = order.vendordepositorderpay_set.all()
    for pay_order in pay_orders_deposit:
        pay_order.delete_deposit()
        pay_order.delete()
    for item in order_items:
        item.delete_order_item(foo=item.id)
        item.delete()
    order.delete()
    return redirect('warehouse_order')

@staff_member_required()
def create_vendor_from_order(request):
    last_order = Order.objects.all().last()
    title = 'Νέος Προμηθευτής'
    if request.POST:
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/τιμολόγια/νέο/')
    else:
        form = VendorForm()

    context = {
        'form':form,
        'title':title,
        'last_order':last_order,
    }

    context.update(csrf(request))
    return render(request,'inventory/new_all_NEW.html',context)

@staff_member_required()
def create_taxes_city(request):
    title = ''
    last_order = Order.objects.all().last()
    if request.POST:
        form = TaxesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/τιμολόγια/προμηθευτής/')
    else:
        form = TaxesForm()
    context = {
        'form': form,
        'title': title,
        'last_order': last_order,
    }
    context.update(csrf(request))
    return render(request,'inventory/new_all_NEW.html',context)

#the main page which you add or remove products in order
@staff_member_required()
def order_edit_id(request, dk):
    title ='Προσθήκη Προϊόντος στο Τιμολόγιο'
    order = Order.objects.get(id=dk)
    order_items = OrderItem.objects.all().filter(order__code = order.code)
    products = Product.objects.all().filter(supplier = order.vendor)
    query = request.GET.get('search_pro')
    if query:
        products = products.filter(
            Q(order_code__contains=query) |
            Q(title__contains=query) |
            Q(sku__contains=query)
        ).distinct()
    context={
        'title':title,
        'order':order,
        'order_items':order_items,
        'products':products,
    }
    return render(request,'inventory/add_product_to_order_NEW.html',context)

@staff_member_required()
def add_product_to_order(request, dk, pk):
    # create a new order item
    product = Product.objects.get(id=pk)
    discount = 0
    if product.order_discount:
        print(product.order_discount, 'hello')
        discount = product.order_discount
    order = Order.objects.get(id=dk)
    products = Product.objects.all().filter(supplier = order.vendor)
    order_items = order.orderitem_set.all()
    unit = Unit.objects.get(name='Τεμάχ')
    fpa = order.vendor.taxes_modifier
    check_if_exists = order_items.filter(product__id=pk)
    if check_if_exists:
        messages.warning(request, 'Το προϊόν υπάρχει ήδη στο τιμολόγιο')
        return redirect('order_edit_main', dk=dk)
    '''
    kept it for reference reason
    order_date = order.date
    date_object = datetime.datetime.strptime('01062016', "%d%m%Y").date()
    if order_date >= date_object:
    '''
    if request.POST:
        form = OrderItemForm(request.POST, initial={'order':order,
                                                    'product':product,
                                                    })
        if form.is_valid():
            new_order_item = form.save()
            form.update_main_product(order_item=new_order_item)
            messages.success(request,' Το προϊον %s καταχωρήθηκε.'%product.title, extra_tags='item_order')
            return HttpResponseRedirect("/αποθήκη/τιμολόγια/επεξεργασία/%s/" %(dk))
    else:
        form = OrderItemForm(initial={'order': order,
                                     'product': product,
                                     'price': product.price_buy,
                                     'discount': discount,
                                     'unit': unit,
                                     'taxes': fpa}
                            )
    context = {
                'title':product.title,
                'order_items':order_items,
                'form':form,
                'order':order,
                'product':product,
                'products':products,
                'image':product.image,
                'return_page':request.META.get('HTTP_REFERER')
            }

    context.update(csrf(request))
    return render(request,'inventory/create_costumer_form.html', context)

@staff_member_required()
def add_product_with_sizes(request, dk, pk):
    order_add_size = True
    product = Product.objects.get(id=pk)
    discount = 0
    if product.order_discount:
        print(product.order_discount, 'hello')
        discount = product.order_discount
    order = Order.objects.get(id=dk)
    order_items = order.orderitem_set.all()
    unit = Unit.objects.get(name='Τεμάχ')
    fpa = order.vendor.taxes_modifier
    sizes = Size.objects.all()
    return_page =order.absolute_url_order()
    unit = Unit.objects.get(name='Τεμάχ')
    if request.POST:
        form = OrderItemForm(request.POST,initial={'order':order, 'product':product, 'qty':0 })
        selected_sizes = request.POST.getlist('check_size')
        print(request.POST)
        if form.is_valid():
            form_order_item = form.save()
            for ele in selected_sizes:
                check_size = SizeAttribute.objects.filter(title__id=int(ele), product_related = product)
                if not check_size:
                    create_size = SizeAttribute.objects.create(title =Size.objects.get(id=int(ele)), product_related=product)
                    create_size.save()
                size_attr = SizeAttribute.objects.get(title=Size.objects.get(id=int(ele)), product_related = product)

                exists = order_items.filter(product=product, size=size_attr)
                if exists:
                    continue
                else:
                    try:
                        qty = request.POST['%s'%(ele)]
                        new_order_item = OrderItem.objects.create(order=order,
                                                                  product=form_order_item.product,
                                                                  unit=form_order_item.unit,
                                                                  discount=form_order_item.discount,
                                                                  taxes=form_order_item.taxes,
                                                                  qty=Decimal(qty),
                                                                  price=form_order_item.price,
                                                                  size= size_attr
                                                                  )
                        new_order_item.save()
                        new_order_item.update_main_product()
                        new_order_item.update_size()
                    except:
                        continue
            OrderItem.objects.filter(size=None).delete()
            return redirect('order_edit_main', dk=dk)
    else:
       form = OrderItemForm(initial={'order': order,
                                     'product': product,
                                     'price': product.price_buy,
                                     'discount': discount,
                                     'unit': unit,
                                     'taxes': fpa,
                                     'qty':0
                                     }
                            )
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/color_size_chart_form.html', context)

@staff_member_required()
def edit_product_from_order(request, dk, pk):
    get_old_item = OrderItem.objects.get(id=pk)
    order_item= OrderItem.objects.get(id=pk)
    products = Product.objects.all().filter(supplier = order_item.order.vendor)
    order_items = OrderItem.objects.all().filter(order__code = order_item.order.code)
    title= order_item.product.title
    query = request.GET.get('search_pro')
    if query:
        products = products.filter(
            Q(description__icontains=query)|
            Q(title__icontains=query)
        ).distinct()
    if request.POST:
        form =OrderItemForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            order_item.update_order_item_from_order(old_item=get_old_item)
            messages.success(request,"Οι αλλαγές αποθηκεύτηκαν")
            return HttpResponseRedirect('/αποθήκη/τιμολόγια/επεξεργασία/%s/' %dk)

    else:
        form =OrderItemForm(instance=order_item)

    context={
        'title':title,
        'order_items':order_items,
        'form':form,
        'order':order_item.order,
        'product':order_item.product,
        'products':products,
        'order_item':order_item,

    }
    context.update(csrf(request))
    return render(request, 'inventory/edit_order_id_New.html',context)

@staff_member_required()
def delete_order_item(request,dk):
    #delete the order_item from the order and transcates the order!
    order_item = OrderItem.objects.get(id=dk)
    order_item.delete_order_item()
    order_item.delete()
    return HttpResponseRedirect("/αποθήκη/τιμολόγια/επεξεργασία/%s/" %(order_item.order.id))

@staff_member_required()
def order_edit(request,dk):
    order = Order.objects.get(id=dk)
    products = order.orderitem_set.all()
    if request.POST:
        form_o =OrderEditForm(request.POST,instance=order)
        if form_o.is_valid():
            form_o.save(commit=False)
            form_o.update_vendor(pk=order.id)
            form_o.save()
            messages.success(request,"Οι αλλαγές αποθηκεύτηκαν")
            return HttpResponseRedirect('/αποθήκη/τιμολόγια/επεξεργασία/%s'%(dk))
    else:
        form_o = OrderEditForm(instance=order)
    title= 'Επεξεργασία,'+ str(order.code)+ ' , ' + str(order.vendor.title)
    return_page ='/αποθήκη/τιμολόγια/επεξεργασία/%s/'%(dk)
    context={
        'title':title,
        'return_page':return_page,
        'form':form_o,
        'products':products,
        'order_id':order,
    }
    context.update(csrf(request))
    return render(request,'inventory/create_costumer_form.html',context)




#this works?
def edit_order(request, dk):
    order = Order.objects.get(id=dk)
    products = order.orderitem_set.all()
    if request.POST:
        form_o =OrderEditForm(request.POST,instance=order)
        if form_o.is_valid():
            form_o.save(commit=False)
            form_o.update_vendor(pk=order.id)
            form_o.save()
            messages.success(request,"Οι αλλαγές αποθηκεύτηκαν")
            return redirect('/')
    else:
        form_o = OrderEditForm(instance=order)
    context={
        'form':form_o,
        'products':products,
        'order_id':order,
    }
    context.update(csrf(request))
    return render(request,'inventory/edit_order.html',context)
#---------------------------------------------------------------------------------------------




