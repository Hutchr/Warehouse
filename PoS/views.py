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

@staff_member_required()
def homepage(request):
    return render(request,'PoS/homepage.html',)

@staff_member_required()
def total_stats(request):
    day = datetime.datetime.today()
    month = datetime.datetime.today().month
    day_orders = RetailOrder.objects.all().filter(day_created = day).order_by('-id')
    day_income = 0
    day_cost = 0
    if day_orders:
        day_income = day_orders.aggregate(Sum('paid_value'))
        day_income = day_income['paid_value__sum']
        day_cost = day_orders.aggregate(Sum('total_cost'))
        day_cost = day_cost['total_cost__sum']

    month_orders = RetailOrder.objects.all().filter(day_created__month =month)
    month_income = 0
    month_cost = 0
    if month_orders:
        month_income = month_orders.aggregate(Sum('paid_value'))
        month_income = month_income['paid_value__sum']
        month_cost = month_orders.aggregate(Sum('total_cost'))
        month_cost = month_cost['total_cost__sum']

    context ={
        'day_income':day_income,
        'day_cost':day_cost,
        'month_income':month_income,
        'month_cost':month_cost,
        'day_orders':day_orders,
    }
    return render(request, 'PoS/total_stats.html', context)

@staff_member_required()
def admin_section(request):
    title = 'admin'
    orders = RetailOrder.objects.filter(order_type__in=['r','b','d']).order_by('-id')
    costumer_accounts = CostumerAccount.objects.filter(is_retail= True)
    payment_method = PaymentMethod.objects.all()

    if request.POST:
        print(request.POST)
    context ={
        'title':title,
        'orders':orders,
        'costumer_accounts':costumer_accounts,
        'payment_method':payment_method,
    }
    return render(request, 'PoS/admin_section.html',context)

# -------------------------------Retail--------------------------------------------------------------------------------
@staff_member_required()
def retail_options(request):
    return render(request,'PoS/lianiki/homepage.html',)

@staff_member_required
def new_retail_order(request):
    get_user = request.user
    new_retail_order = RetailOrder.objects.create(costumer_account=CostumerAccount.objects.get(id=1),
                                                    seller_account=get_user,
                                                    order_type='r',
                                                    status=Order_status.objects.get(id=1),
                                                    payment_method=PaymentMethod.objects.get(id=1))
    new_retail_order.save()
    return HttpResponseRedirect('/PoS/lianiki/order/%s' %(new_retail_order.id))

#main retail view
@staff_member_required()
def retail_main_page(request, dk):
    payments_method = PaymentMethod.objects.all()
    costumers = CostumerAccount.objects.filter(is_retail=True, is_eshop=False)
    products = None
    retail_order = RetailOrder.objects.get(id=dk)
    order_items = retail_order.order_items()
    categories = Category.objects.all()
    search_products = request.GET.get('search_products')
    if search_products:
        products = Product.my_query.active_warehouse()
        products = products.filter(
            Q(title__icontains=search_products) |
            Q(order_code__icontains=search_products) |
            Q(barcode__icontains =search_products) |
            Q(brand__title__icontains =search_products) |
            Q(supplier__title__icontains = search_products)
        ).distinct()
    if 'payment' in request.POST:
        order_change_payment_method(request, retail_order)
    if 'costumer' in request.POST:
        order_change_costumer(request, retail_order=retail_order)
    query = request.GET.get('search_pro')
    if query:
        categories = categories.filter(title__icontains =query)
    context = {
        'currency':CURRENCY,
        'categories':categories,
        'order':retail_order,
        'products':products,
        'order_items':order_items,
        'costumers':costumers,
        'payments_method':payments_method,
        }
    return render(request, 'PoS/lianiki/show_categories_lianiki.html', context)

@staff_member_required
def retail_category_page(request,dk,pk):
    retail_order = RetailOrder.objects.get(id=dk)
    payments_method = PaymentMethod.objects.all()
    costumers = CostumerAccount.objects.filter(is_retail=True, is_eshop=False)
    order_items = retail_order.order_items()
    category = Category.objects.get(id=pk)
    products = Product.my_query.active_warehouse().filter(category__title=category.title)
    search_products = request.GET.get('search_products')
    if search_products:
        products = products.filter(
            Q(title__icontains = search_products) |
            Q(description__icontains= search_products) |
            Q(product_id__icontains =search_products) |
            Q(supplier__title__icontains=search_products)
        ).distinct()
    if 'payment' in request.POST:
        order_change_payment_method(request, retail_order)
    if 'costumer' in request.POST:
        order_change_costumer(request, retail_order=retail_order)
    context = {
        'payments_method': payments_method,
        'costumers': costumers,
        'categories': category,
        'order': retail_order,
        'products': products,
        'order_items': order_items,
        'currency': CURRENCY,
    }
    return render(request,'PoS/lianiki/lianiki_category.html', context)

@staff_member_required
def add_product_to_order_auto(request, dk,pk):
    retail_order = RetailOrder.objects.get(id=dk)
    product = Product.objects.get(id=pk)
    new_order_item = RetailOrderItem.objects.create(title=product,
                                                    order=retail_order,
                                                    cost=product.price_buy,
                                                    price=product.site_price,
                                                    qty=1)
    new_order_item.save()
    new_order_item.add_item_auto()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required
def retail_add_product(request,dk,pk):
    product = Product.objects.get(id=pk)
    order = RetailOrder.objects.get(id=dk)
    order_items = order.order_items()
    product_colors = None
    product_size = None
    if request.POST:
        form  = RetailAddForm(request.POST, initial={'order':order, 'price':product.site_price, 'title': product,'cost':product.price_buy, })
        if form.is_valid():
            form.save()
            form.add_item(order=order, product=product)
            return redirect('retail_order_section', dk=dk)
    else:
        form = RetailAddForm(initial={'order':order, 'price':product.site_price, 'title': product, 'cost':product.price_buy, })

    context = {
        'form':form,
        'order_items':order_items,
        'order':order,
        'product':product,
        'product_size':product_size,
        'products_colors':product_colors,

    }
    return render(request,'PoS/lianiki/lianiki_add_product.html', context)

@staff_member_required
def retail_choose_size_page(request,dk, pk):
    retail = True
    product = Product.objects.get(id=pk)
    order = RetailOrder.objects.get(id=dk)
    sizes = product.sizes
    if request.POST:
        for size in sizes:
            size_qty = request.POST.get('%s'%(size.id))
            try:
                if float(size_qty) > 0:
                    create_retail_item = RetailOrderItem.objects.create(title=product,
                                                                          order=order,
                                                                          cost=product.price_buy,
                                                                          price = product.site_price,
                                                                          qty =size_qty,
                                                                          size=size
                                                                          )
                    create_retail_item.save()
                    create_retail_item.update_order_and_warehouse_with_size()
                    messages.success(request, 'το προϊόν %s με %s μεγεθος προστέθηκε.'%(product, size))
            except:
                continue

        return redirect('retail_order_section', dk=dk)
    return_page = request.META.get('HTTP_REFERER')
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required
def retail_edit_order_item(request, dk, pk):
    order_item = RetailOrderItem.objects.get(id=pk)
    old_order_price = order_item.price
    old_order_qty = order_item.qty
    old_cost = order_item.cost
    if request.POST:
        form = RetailAddForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            form.edit_item(order_item=order_item, old_price=old_order_price, old_qty=old_order_qty, old_cost=old_cost)
            return redirect('retail_order_section', dk=dk)
    else:
        form = RetailAddForm(instance=order_item)
    context = {
        'form':form,
        'order':order_item.order,
        'order_item':order_item,
    }
    context.update(csrf(request))
    return render(request, 'PoS/lianiki/lianiki_add_product.html' , context)

@staff_member_required
def activate_deactivate_taxes(request,dk):
    order = RetailOrder.objects.get(id=dk)
    if order.taxes == 24:
        order.taxes = 0
    else:
        order.taxes = 24
    order.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required
def pos_create_new_costumer(request,dk):
    retail_order = RetailOrder.objects.get(id=dk)
    if request.POST:
        form = CreateCostumerPosForm(request.POST,initial={'is_eshop':False})
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/PoS/lianiki/order/%s/'%(dk))

    else:
        form = CreateCostumerPosForm()

    context = {
        'form': form,
        'order': retail_order,
    }
    context.update(csrf(request))
    return render(request, 'PoS/pos_create_user.html', context)

@staff_member_required
def pos_edit_order(request,dk):
    retail_order =RetailOrder.objects.get(id=dk)
    if request.POST:
        form = RetailEditForm(request.POST, instance=retail_order)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('PoS/lianiki/order/%s/'%(dk))
    else:
        form =RetailEditForm(instance=retail_order)
    context={
        'form':form,
        'order':retail_order,
        'title':'Επεξεργασία %s'%(retail_order.title),
        'return_page':'PoS/lianiki/order/%s/'%(dk),
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required
def retail_delete_order_item(request,dk,pk,):
    order_item = RetailOrderItem.objects.get(id=pk)
    order_item.delete_from_order()
    order_item.delete()
    return redirect('retail_order_section', dk=dk)

@staff_member_required
def delete_order(request, dk):
    order = RetailOrder.objects.get(id=dk)
    order_items = order.retailorderitem_set.all()
    for item in order_items:
        item.delete_from_order(dk=dk)
    order.delete()
    return HttpResponseRedirect('/PoS/')

@staff_member_required
def create_return_order(request):
    get_user = request.user
    new_retail_order = RetailOrder.objects.create(costumer_account=CostumerAccount.objects.get(id=1),
                                                    seller_account=get_user,
                                                    order_type='b',
                                                    status=Order_status.objects.get(id=1),
                                                    payment_method=PaymentMethod.objects.get(id=1))
    new_retail_order.save()
    return redirect('retail_order_section', dk=new_retail_order.id)

@staff_member_required
def lianiki_order_pay_not_complete(request, dk):
    order = RetailOrder.objects.get(id=dk)
    order.status = Order_status.objects.get(id=3)
    old_value = order.paid_value #gets the current paid_value
    if request.POST:
        form = PayRetailForm(request.POST, instance=order)
        if form.is_valid():
            costumer = order.costumer_account
            costumer.paid_value -= old_value
            costumer.paid_value += Decimal(request.POST.get('paid_value'))
            costumer.balance -= (Decimal(request.POST.get('paid_value')) - old_value)
            costumer.save()
            #form.update_costumer(order=order)
            form.save()
            return HttpResponseRedirect('/PoS/lianiki/order/%s/' %(dk))
    else:
        form =PayRetailForm(instance=order,initial={'paid_value':order.value})

    context ={
        'form':form,
        'order':order,
    }
    context.update(csrf(request))

    return render(request, 'PoS/lianiki/lianiki_add_product.html', context)

@staff_member_required
def lianiki_print_order_to_warehouse(request):
    '''
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
    '''
    pass

@staff_member_required
def lianiki_order_closed(request,dk):
    order = RetailOrder.objects.get(id= dk)
    close_order(request, order)
    return HttpResponseRedirect('PoS/lianiki/')


def destroy_order(request):
    new_destroy_order  = DestroyOrder.objects.create()
    new_destroy_order.save()
    return redirect('pos_destroy_order', dk=new_destroy_order.id)

def destroy_order_products(request,dk):
    destroy_order = DestroyOrder.objects.get(id=dk)
    destroy_order_items = destroy_order.destroyorderitem_set.all()
    products = Product.objects.all().filter(ware_active = True)
    vendors = Supply.objects.all()
    categories = Category.objects.all()
    vendor_name = None
    category_name = None
    query = request.GET.get('search_pro')
    if query:
        products = products.filter(
            Q(title__icontains = query)|
            Q(description__icontains=query)|
            Q(product_id__icontains =query)|
            Q(supplier__title__icontains = query)
        ).distinct()
    if request.POST:
        vendor_name = request.POST.getlist('vendor')
        category_name = request.POST.getlist('category')
        if vendor_name:
            products = products.filter(supplier__title__in =vendor_name)
        if category_name:
            products =products.filter(category__title__in=category_name)
    context ={
        'order':destroy_order,
        'order_items':destroy_order_items,
        'products':products,
        'title':'Καταστροφές',
        'category_name':category_name,
        'vendor_name':vendor_name,
        'vendors':vendors,
        'categories':categories,
        'destroy':True,
    }
    return render(request, 'PoS/lianiki/return_products.html', context)

def destroy_order_item_auto(request, dk, pk):
    order = DestroyOrder.objects.get(id=dk)
    product = Product.objects.get(id=pk)
    create_item = DestroyOrderItem.objects.create(title=product,
                                                  order=order,
                                                  cost=product.final_price_warehouse(),
                                                  qty=1,
                                                  )
    create_item.save()
    product.qty -=1
    product.save()
    order.total_cost += create_item.cost * create_item.qty
    order.save()
    messages.success(request, 'Προστέθηκε το προϊόν %s'%(product.title))
    return redirect('pos_destroy_order', dk=dk)

def destroy_order_item_id(request,dk,pk):
    order = DestroyOrder.objects.get(id=dk)
    product = Product.objects.get(id =pk)
    product_sizes = product.sizes
    if request.POST:
        form = DestroyOrderItemForm(request.POST, initial={'order':order, 'title':product})
        if form.is_valid():
            form.save()
            form.update_order_and_warehouse(order=order, product=product)
            return HttpResponseRedirect('/PoS/destroy-order/%s'%(dk))
    else:
        form = DestroyOrderItemForm(initial={'order':order, 'title':product,'cost':product.final_price_warehouse()})
    context={
        'destroy':'boolean',
        'form':form,
        'order':order,
        'products_sizes':product_sizes,
        'product':product,
    }
    return render(request, 'PoS/lianiki/return_product_id.html',context)

def destroy_order_item_delete(request,dk,pk):
    order_item = DestroyOrderItem.objects.get(id=pk)
    order = DestroyOrder.objects.get(id=dk)
    order_item.delete_order_item(order=order, order_item=order_item)
    if order_item.color:
        order_item.delete_order_item_with_color()
    order_item.delete()
    return HttpResponseRedirect('/PoS/destroy-order/%s'%(dk))

def destroy_order_item_edit(request,dk,pk):
    products=Product.objects.all().filter(ware_active='a')
    order = DestroyOrder.objects.get(id=dk)
    destroy_order_item = DestroyOrderItem.objects.get(id=pk)
    if request.POST:
        form =DestroyOrderItemForm(request.POST,instance=destroy_order_item)
        if form.is_valid():
            form.save(commit=False)
            form.edit_order_and_warehouse(dk=dk, pk=pk)
            form.save()
            return HttpResponseRedirect('/PoS/destroy-order/%s'%(dk))
    else:
        form = DestroyOrderItemForm(instance=destroy_order_item)
    context={
        'products':products,
        'product':destroy_order_item,
        'destroy':'boolean',
        'order':order,
        'form':form,
    }
    context.update(csrf(request))
    return render(request,'PoS/lianiki/return_product_id.html', context)






#-------------------Eshop Section-------------------------------------------------------------------------------------

