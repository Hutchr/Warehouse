from django.shortcuts import render,redirect, HttpResponseRedirect , render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from PoS.models import *
from inventory_manager.form import *
from .models import Product, Supply, Category, CURRENCY, ProductPhotos, RelatedProducts, SameColorProducts
from transcations.models import *
from tools.models import ToolsTableOrder, Discount
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
def http_referer(request):
    return request.META.get('HTTP_REFERER')



#----------------Tools---------------------------
@staff_member_required()
def tools(request):
    color = Color.objects.all().order_by('title')
    size = Size.objects.all().order_by('-title')
    payment_method= PaymentMethod.objects.all()
    payment_group = PaymentMethodGroup.objects.all()
    categories = Category.objects.all()
    site_categories = CategorySite.objects.all()
    brands = Brands.objects.all()
    if request.POST:
        color_form = CreateColor(request.POST)
        size_form = CreateSize(request.POST)
        payment_group_form = PaymentGroupForm(request.POST)
        payment_form = PaymentForm(request.POST)
        #categories_form = CategoryForm(request.POST)
        if 'size_submit' in request.POST:
             if size_form.is_valid():
                size_form.save()
                title = size_form.cleaned_data['title']
                messages.success(request, 'Το χρώμα %s προστέθηκε'%(title))
                return HttpResponseRedirect('/αποθήκη/εργαλεία/')
        elif 'group_submit' in request.POST:
                if payment_group_form.is_valid():
                    payment_group_form.save()
                    title = payment_group_form.cleaned_data['title']
                    messages.success(request,'Ο τρόπος πληρωμής  %s προστέθηκε.'%(title))
                    return HttpResponseRedirect('/αποθήκη/εργαλεία/')
        else:
            if color_form.is_valid():
                color_form.save()
                title = color_form.cleaned_data['title']
                messages.success(request, 'Το χρώμα %s προστέθηκε'%(title))
                return HttpResponseRedirect('/αποθήκη/εργαλεία/')

            elif payment_form.is_valid():
                    payment_form.save()
                    title = payment_form.cleaned_data['title']
                    messages.success(request,'Ο τρόπος πληρωμής  %s προστέθηκε.'%(title))
                    return HttpResponseRedirect('/αποθήκη/εργαλεία/')

    else:
        color_form = CreateColor()
        size_form = CreateSize()
        payment_form =PaymentForm()
        payment_group_form = PaymentGroupForm()

    context = {
        'color':color,
        'size':size,
        'color_form':color_form,
        'size_form':size_form,
        'payment_form':payment_form,
        'payment_group_form':payment_group_form,
        'payment_method':payment_method,
        'payment_group':payment_group,
        'categories':categories,
        'site_categories':site_categories,
        'title':'Κατηγορίες',
        'brands':brands,

    }
    context.update(csrf(request))
    return render(request,'inventory/tools.html',context)

@staff_member_required()
def tools_add_edit_brand(request,dk=None):
    if dk:
        brand = Brands.objects.get(id=dk)
        if request.POST:
            form = BrandForm(request.POST, instance=brand)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/αποθήκη/εργαλεία/')
        else:
            form = BrandForm(instance=brand)
        title='Δημιουργία Brand'
        return_page ='/αποθήκη/εργαλεία/'

        context={
            'form':form,
            'title':title,
            'return_page':return_page
        }
        context.update(csrf(request))
        return render(request, 'inventory/create_costumer_form.html', context)


    if request.POST:
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form = BrandForm()
    title='Δημιουργία Brand'
    return_page ='/αποθήκη/εργαλεία/'

    context={
        'form':form,
        'title':title,
        'return_page':return_page
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_edit_category(request, dk):
    category=Category.objects.get(id=dk)
    if request.POST:
        form =CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,'H Κατηγορία %s επεξεργάστηκε.'%(category))
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form =CategoryForm(instance=category)

    context={
        'form':form,
        'title':category.title,
        'return_page':'/αποθήκη/εργαλεία/',
    }
    context.update(csrf(request))
    return render(request,'inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_new_category(request):
    if request.POST:
        form =CategoryForm(request.POST,)
        if form.is_valid():
            form.save()
            messages.success(request,'H Κατηγορία δημιουργήθηκε.')
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form =CategoryForm()
    context={
        'form':form,
        'title':'Δημιουργία Κατηγορίας',
        'return_page':'/αποθήκη/εργαλεία/',
    }
    context.update(csrf(request))
    return render(request,'inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_edit_category_site(request, dk):
    category = CategorySite.objects.get(id=dk)
    if request.POST:
        form =CategorySiteForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,'H Κατηγορία %s επεξεργάστηκε.'%(category))
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form = CategorySiteForm(instance=category)
    context={
        'form':form,
        'title':category.title,
        'return_page':'/αποθήκη/εργαλεία/',

    }
    context.update(csrf(request))
    return render(request,'inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_new_category_site(request):
    if request.POST:
        form = CategorySiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'H Κατηγορία δημιουργήθηκε.')
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form = CategorySiteForm()

    context={
        'form':form,
        'title':'Δημιουργία Κατηγορίας',
        'return_page':'/αποθήκη/εργαλεία/',
    }
    context.update(csrf(request))
    return render(request,'inventory/create_costumer_form.html', context)

@staff_member_required()
def activate_or_deactive_color(request, dk):
    color = Color.objects.get(id=dk)
    if color.status == 'a':
        color.status = 'b'
        messages.warning(request,'To %s απενεργοποιήθηκε'%(color.title))
    else:
        messages.success(request,'To %s ενεργοποιήθηκε'%(color.title))
        color.status = 'a'
    color.save()
    return HttpResponseRedirect('/αποθήκη/εργαλεία/')

@staff_member_required()
def tools_edit_color(request,dk):
    color = Color.objects.get(id=dk)

    if request.POST:
        form = CreateColor(request.POST, instance=color)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form = CreateColor(instance=color)

    context = {
        'form':form,
    }

    return render(request, 'inventory/tools_edit_color.html', context)

@staff_member_required()
def tools_edit_size(request,dk):
    size = Size.objects.get(id=dk)
    if request.POST:
        form = CreateSize(request.POST, instance=size)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form = CreateSize(instance=size)
    context = {
        'form': form,
    }
    return render(request, 'inventory/tools_edit_color.html', context)

@staff_member_required()
def edit_payment_group(request, dk):
    payment_group =PaymentMethodGroup.objects.get(id=dk)
    if request.POST:
        form = PaymentGroupForm(request.POST, instance=payment_group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form = PaymentGroupForm(instance=payment_group)
    context ={
        'form':form,
    }
    context.update(csrf(request))
    return render(request, 'inventory/tools_edit_color.html', context)

@staff_member_required()
def edit_payment(request, dk):
    payment=PaymentMethod.objects.get(id=dk)
    if request.POST:
        form = PaymentGroupForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/εργαλεία/')
    else:
        form = PaymentForm(instance=payment)

    context ={
        'form':form,
    }
    context.update(csrf(request))
    return render(request, 'inventory/tools_edit_color.html', context)

@staff_member_required()
def activate_deactivate_size(request,dk):
    size = Size.objects.get(id=dk)
    if size.status == 'a':
        size.status = 'b'
    else:
        size.status = 'a'
    size.save()
    return HttpResponseRedirect('/αποθήκη/εργαλεία/')

@staff_member_required()
def tools_characteristics(request):
    characteristics = Characteristics.objects.all()
    characteristics_value = CharacteristicsValue.objects.all()
    get_data = request.POST.get('search_pro')
    if get_data:
        characteristics = characteristics.filter(title__icontains = get_data)
        characteristics_value = characteristics_value.filter(title__icontains = get_data)
    context = {
        'title':'Χαρακτηριστικα',
        'char':characteristics,
        'char_value':characteristics_value
    }
    context.update(csrf(request))
    return render_to_response('inventory/tools_char.html', context)

@staff_member_required()
def tools_create_char(request):
    if request.POST:
        form = CharForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tools_char')
    else:
        form = CharForm()
    context = {
        'title':'Δημιουργια Χαρακτηριστικού',
        'form':form,
        'return_page':http_referer(request)
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_edit_char(request, dk):
    char = Characteristics.objects.get(id = dk)
    if request.POST:
        form = CharForm(request.POST, instance=char)
        if form.is_valid():
            form.save()
            return redirect('tools_char')
    else:
        form = CharForm(instance=char)
    context = {
        'title': 'Επεξεργασία %s'%(char.title),
        'form': form,
        'return_page': http_referer(request)
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_delete_char(request, dk):
    char = Characteristics.objects.get(id=dk)
    get_products_char = ProductCharacteristics.objects.filter(title = char)
    for get_char in get_products_char:
        get_char.delete()
    char.delete()
    return HttpResponseRedirect(http_referer(request))

@staff_member_required()
def tools_create_char_val(request):
    if request.POST:
        form = CharValForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tools_char')
    else:
        form = CharValForm()
    context = {
        'title':'Δημιουργια Χαρακτηριστικού',
        'form':form,
        'return_page':http_referer(request)
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_edit_char_val(request, dk):
    char = CharacteristicsValue.objects.get(id = dk)
    if request.POST:
        form = CharValForm(request.POST, instance=char)
        if form.is_valid():
            form.save()
            return redirect('tools_char')
    else:
        form = CharValForm(instance=char)
    context = {
        'title':'Επεξεργασία %s'%(char.title),
        'form':form,
        'return_page':http_referer(request)
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html', context)

@staff_member_required()
def tools_delete_char_val(request, dk):
    char = CharacteristicsValue.objects.get(id=dk)
    get_products_char = ProductCharacteristics.objects.filter(description = char)
    for get_char in get_products_char:
        get_char.delete()
    char.delete()
    return HttpResponseRedirect(http_referer(request))

@staff_member_required()
def tools_change_order(request):
    orders = ChangeQtyOrder.objects.all()
    title ='Αλλαγή Ποσότητας'
    if request.POST:
        form = ChangeQtyOrderForm(request.POST)
        if form.is_valid():
            form.save()
            new_order = ChangeQtyOrder.objects.last().id
            return HttpResponseRedirect('/αποθήκη/εργαλεία/αλλαγή-ποσότητας/%s' %(new_order))
    else:
        form  = ChangeQtyOrderForm()
    context = locals()
    context.update(csrf(request))
    return render(request,'inventory/tools_order.html', context)

@staff_member_required()
def tools_change_qty(request, dk):
    order = get_object_or_404(ChangeQtyOrder, id=dk)
    order_items = ChangeQtyOrderItem.objects.all().filter(order=order)
    vendors = Supply.objects.all()
    categories = Category.objects.all()
    products = None
    products_color = None
    products_size = None
    title = order.title
    vendor_name = None
    category_name = None
    if request.POST:
        vendor_name = request.POST.getlist('vendor')
        category_name = request.POST.getlist('category')
        search_name = request.POST.get('search_name')
        products = Product.my_query.active_warehouse()
        if vendor_name:
            products = products.filter(supplier__title__in=vendor_name,)
        if category_name:
            products = products.filter(category__title__in=category_name)
        if search_name:
            products = products.filter(
                Q(title__icontains=search_name) |
                Q(category__title__icontains=search_name) |
                Q(supplier__title__icontains=search_name) |
                Q(order_code__icontains=search_name)).distinct()
    context = {
        'title': title,
        'products': products,
        'vendors': vendors,
        'vendor_name': vendor_name,
        'categories': categories,
        'category_name': category_name,
        'order_item': order_items,
        'order': order,
        'product_color': products_color,
        'product_size': products_size,
    }
    return render(request,'inventory/tools_change_qty.html',context)

@staff_member_required()
def tools_grab_qty(request, dk, pk):
    order = ChangeQtyOrder.objects.get(id=dk)
    order_items = ChangeQtyOrderItem.objects.all().filter(order=order)
    product = Product.objects.get(id=pk)
    if request.POST:
        form = ChangeQtyOrderItemForm(request.POST, initial={'title': product, 'order': order})
        if form.is_valid():
            form.save()
            form.update_product(product=product)
            messages.success(request,'Επιτυχής αλλαγή ποσότητας')
            return HttpResponseRedirect('/αποθήκη/εργαλεία/αλλαγή-ποσότητας/%s' % order.id)
    else:
        form = ChangeQtyOrderItemForm(initial={'title': product, 'order': order})
    context = {
        'form': form,
        #'title':title,
        'order_item': order_items,
        'order': order,
    }
    context.update(csrf(request))
    return render(request, 'inventory/tools_grab_qty.html', context)


@staff_member_required()
def tools_grab_size(request, dk, pk):
    order = get_object_or_404(ChangeQtyOrder, id=dk)
    order_items = ChangeQtyOrderItem.objects.all().filter(order=order)
    size = get_object_or_404(SizeAttribute, id=pk)
    if request.POST:
            form = ChangeQtyOrderItemForm(request.POST, initial={'title': size.product_related, 'order': order, 'size': size})
            if form.is_valid():
                form.save()
                form.update_size(size=size)
                messages.success(request, 'Επιτυχής αλλαγή ποσότητας')
                return HttpResponseRedirect('/αποθήκη/εργαλεία/αλλαγή-ποσότητας/%s' % order.id)
    else:
        form = ChangeQtyOrderItemForm(initial={'title': size.product_related,
                                                'order': order,
                                                'size': size})
    context = {
        'form': form,
        #'title':title,
        'order_item': order_items,
        'order': order,
    }
    context.update(csrf(request))
    return render(request, 'inventory/tools_grab_qty.html',context)

@staff_member_required()
def tools_discount_page(request):
    currency = CURRENCY
    title = 'Μαζικές Εκπτώσεις'
    discounts_orders = Discount.objects.all()
    brands = Brands.objects.all()
    category = Category.objects.all()
    vendors = Supply.objects.all()
    products = None
    if request.GET:
        products = Product.my_query.active_warehouse()
        category_name = request.GET.getlist('category_name')
        vendor_name = request.GET.getlist('vendor_name')
        offer_name = request.GET.get('offer_name')
        products = products.filter(category__id__in=category_name) if category_name else products
        products = products.filter(supply__id__in=vendor_name) if vendor_name else products
        #products = products.filter()

    if request.POST:
        get_products = request.POST.getlist('get_products')
        title = request.POST.get('title')
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
        type_of = request.POST.get('type_of')
        final_price = request.POST.get('final_price')
        active = request.POST.get('active')
        try:
            new_discount_order = Discount.objects.create(title=title,
                                                         active=active,
                                                         date_start=date_start,
                                                         date_end=date_end,
                                                         type_of_discount=type_of,
                                                         value=Decimal(final_price)
                                                         )
            new_discount_order.save()
            for ele in get_products:
                new_discount_order.query_set.add(Product.objects.get(id=ele))
                new_discount_order.save()
            messages.success(request, 'Η έκπτωση δημιουργήθηκε')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except:
            messages.warning(request, 'Something goes bad!')

    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/tools_discount.html', context)

@staff_member_required
def discount_order_specific(request, dk):
    brands = Brands.objects.all()
    category = Category.objects.all()
    vendors = Supply.objects.all()
    specific_order = True
    discounts_orders = Discount.objects.all()
    get_order = get_object_or_404(Discount, id=dk)
    title = 'Μαζικές Eκπτώσεις - %s' % get_order
    if request.GET:
        products = Product.my_query.active_warehouse()
        category_name = request.GET.getlist('category_name')
        vendor_name = request.GET.getlist('vendor_name')
        offer_name = request.GET.get('offer_name')
        products = products.filter(category__id__in=category_name) if category_name else products
        products = products.filter(supply__id__in=vendor_name) if vendor_name else products
    if request.POST:
        print(request.POST)
        get_old_items = request.POST.getlist('add_items')
        get_products = request.POST.getlist('get_products')
        title = request.POST.get('title')
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
        type_of = request.POST.get('type_of')
        final_price = request.POST.get('final_price')
        active = request.POST.get('active')
        get_order.query_set.clear()
        if get_old_items:
            for item in get_old_items:
                get_order.query_set.add(Product.objects.get(id=item))
                get_order.save()
                messages.success(request,'Τα προϊόντα που επιλέξατε αφαιρέθηκαν ')
        if get_products:
            for item in get_products:
                get_order.query_set.add(Product.objects.get(id=item))
                get_order.save()
        get_order.title = title
        get_order.date_start = date_start
        get_order.date_end = date_end
        get_order.type_of_discount = type_of
        get_order.value = final_price
        get_order.active = active
        get_order.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/tools_discount.html', context)

def discount_order_delete(request, dk):
    pass


def site_tools(request):
    pass

def import_export_controller(request):
    pass