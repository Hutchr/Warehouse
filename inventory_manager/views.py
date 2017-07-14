from django.shortcuts import render,HttpResponseRedirect, redirect
from products.models import *
from inventory_manager.models import *
from .form import *
from django.core.context_processors import csrf
from django.contrib import messages
from django.core.urlresolvers import reverse

def homepage(request):
    return render(request,'inventory_homepage.html')

def vendors(request):
    vendors=Supply.objects.all().order_by('title')
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Its done")

        else:
            messages.error(request,"Something goes wrong!")

    else:
        form = VendorForm()
    args={}
    args['vendors'] = vendors
    args['form']=form
    args.update(csrf(request))
    return render(request,'vendor/vendors.html',args)

def vendors_edit(request):
    vendors = Supply.objects.all().order_by('title')
    context ={
        'vendors':vendors,
    }
    return render(request,'vendor/edit_vendors.html',context)



def vendors_edit_id(request,dk):
    vendors=Supply.objects.all().order_by('title')
    vendor = Supply.objects.get(id=dk)

    if request.POST:
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request,"The vendor is updated!")
    else:
        form = VendorForm(instance=vendor)

    context ={
           'form':form,
           'vendors':vendors,
           'vendor':vendor
    }
    return render(request,'vendor/edit_vendor_id.html',context)



def vendors_details(request):
    vendors = Supply.objects.all().order_by('title')

    context ={
        'vendors':vendors,
    }
    return render(request,'vendor/vendor_details.html',context)

def vendor_analytics(request, dk):
    vendors = Supply.objects.all().order_by('title')
    vendor = Supply.objects.get(id=dk)


    context = {
        'vendors':vendors,
        'vendor':vendor,

    }
    return render(request,'vendor/vendor_analytics.html', context)








def products(request):
    category = Category.objects.all().order_by('title')
    vendors = Supply.objects.all().order_by('title')
    if request.method =='POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Its Done!")
            return HttpResponseRedirect('')
    else:
        form = ProductForm()

    args={}
    args['form'] =form
    args['category'] = category
    args['vendors'] = vendors
    args.update(csrf(request))



    return render(request,'products/products.html',args)


def edit_product_vendor(request,dk):
    category = Category.objects.all().order_by('title')
    vendors = Supply.objects.all().order_by('title')
    vendor = Supply.objects.get(id=dk)
    products =vendor.product_set.all()
    context={
        'category':category,
        'vendor':vendor,
        'vendors':vendors,
        'products':products
    }
    return render(request,'products/edit_product_vendor.html',context)



def edit_product_vendor_id(request):
    pass


def edit_product(request):
    category = Category.objects.all().order_by('title')
    vendors = Supply.objects.all().order_by('title')
    products =Product.objects.all().order_by('title')
    context = {
        'category':category,
        'vendors':vendors,
        'products':products,
    }
    return render(request,'products/edit_products.html',context)

def edit_products_category(request,dk):
    cate =Category.objects.get(id=dk)
    category = Category.objects.all().order_by('title')
    vendors = Supply.objects.all().order_by('title')
    products = Product.objects.filter(category_id=dk)
    context={
        'category':category,
        'vendors':vendors,
        'cate':cate,
        'products':products,
    }
    return render(request,'products/edit_products_category.html',context)

def edit_product_id(request,dk):
    product =Product.objects.get(id=dk)
    if request.POST:
        form= ProductForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
            messages.success(request,"Το προϊόν ενημερώθηκε")
    else:
        form=ProductForm(instance=product)



    context={
        'form':form,
        "product":product
    }
    context.update(csrf(request))
    return render(request,'products/edit_product_id.html',context)










#----------------------------------------------------------------------------------------------------#

def movements(request):
    vendors = Supply.objects.all().order_by('title')

    if request.POST:
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Order its done.")
            return HttpResponseRedirect('/inventory/movements/new_order/add_product/')
    else:
        form = OrderForm()

    args={
        'form':form,
        'vendors':vendors,
    }
    args.update(csrf(request))

    return render(request,'movements/movements.html',args)



def add_product_to_order(request):
    order = Order.objects.all().last()
    products = OrderItem.objects.filter(order__id=order.id)
    if request.POST:
        form = OrderItemForm(request.POST,initial={'order':order})
        if form.is_valid():
            form.update_order()
            form.update_stock()
            messages.success(request,"Item added to Order")
            form.save()
    else:
        form=OrderItemForm(initial={'order':order})
    context={
        'products':products,
        'order':order,
        'form':form
    }
    context.update(csrf(request))
    return render(request,'movements/add_product_to_form.html',context)



def all_orders(request):
    vendors = Supply.objects.all().order_by('title')
    orders = Order.objects.all().order_by('date')
    context ={
        'vendors': vendors,
        'orders': orders,
    }
    return  render(request,'movements/all_orders.html',context)

def all_orders_vendor(request,dk):
    vendor =Supply.objects.get(id=dk)
    orders =vendor.order_set.all()
    context={
        'vendor':vendor,
        'orders':orders
    }
    return render(request,'movements/all_orders_vendor.html',context)

def all_order_id(request,dk):
    order = Order.objects.get(id=dk)
    products = order.orderitem_set.all()
    context={
        'order':order,
        'products':products
    }
    return render(request,'movements/all_order_id.html',context)

def edit_order(request):
    vendors = Supply.objects.all().order_by('title')
    orders =Order.objects.all().order_by('-date')[0:20]
    context ={
        'vendors':vendors,
        'orders':orders,
    }
    return render(request,'movements/edit_orders.html',context)



def edit_order_vendor(request,dk):
    vendors = Supply.objects.all().order_by('title')

    vendor =Supply.objects.get(id=dk)
    orders =vendor.order_set.all()
    
    context={
        'vendors':vendors,
        'vendor':vendor,
        'orders':orders
    }
    return render(request,'movements/edit_order_vendor.html',context)




def edit_order_id(request,dk):
    order = Order.objects.get(id=dk)
    if request.POST:
        form = OrderForm(request.POST,instance=order)
        if form.is_valid():
            messages.success(request,'Οι μετατροπές αποθηκεύτηκαν.')
            form.save()
    else:
        form =OrderForm(instance=order)
    order = Order.objects.get(id=dk)
    products =order.orderitem_set.all()
    context={
        'form':form,
        'order':order,
        'products':products,
    }
    context.update(csrf(request))
    return render(request, 'movements/edit_order_id.html',context)






def edit_item_order_id(request,dk):
    item =OrderItem.objects.get(id=dk)
    if request.POST:
        form = OrderItemForm(request.POST,instance=item)
        if form.is_valid():
            form.modify_stock(item.id)
            form.modify_order(item.id)
            form.save()
    else:
        form = OrderItemForm(instance=item)

    args={}
    args['form'] =form
    args.update(csrf(request))
    return render(request,'movements/edit_item_order_id.html',args)


def delete_order(request,dk):
    order = Order.objects.get(dk -id)
    order.delete()
    messages.success(request,'<a href> {{ order.title }} has deleted. </a>')
    return redirect(request,'')

def movements_analytics(request):
    vendors = Supply.objects.all()
    orders =Order.objects.all().order_by('date')[0:5]
    context = {
        'vendors':vendors,
        'orders':orders,
    }
    return render(request,'movements/movements_analytics.html',context)

