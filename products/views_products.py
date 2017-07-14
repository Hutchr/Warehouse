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
from django.contrib import messages
from django.db.models import Q

def http_referer(request):
    return request.META.get('HTTP_REFERER')

@staff_member_required()
def homepage(request):
    #warehouse main page
    products = Product.objects.all().order_by('-id')[0:5]
    vendors = Supply.objects.all().order_by('-id')[0:5]
    orders = Order.objects.all().order_by('-id')[0:5]
    last_order = Order.objects.last()
    title = 'Αποθήκη'
    context = {
        'products': products,
        'vendors': vendors,
        'title': title,
        'orders': orders,
        'last_order': last_order,
        'currency': CURRENCY,
    }
    return render(request, 'inventory/homepageNew.html', context)

@staff_member_required()
def products(request):
    #get the user input date or the default
    currency = CURRENCY
    title='Προϊόντα'
    products = Product.objects.all()
    categories = Category.objects.all()
    categories_site = CategorySite.objects.all()
    vendors = Supply.objects.all()
    table_control_order = ToolsTableOrder.objects.get(title='warehouse_table_product_order')
    #get session data
    try:
        category = request.session['pro_cat_fi']
    except:
        request.session['pro_cat_fi'] = ''
        category = None
    try:
        category_site = request.session['pro_cat_site']
    except:
        request.session['pro_cat_site'] = ''
        category_site = None
    try:
        vendor = request.session['pro_ven_fi']
    except:
        request.session['pro_ven_fi']= ''
        vendor = None
    try:
        site_status = request.session['pro_site_fi']
    except:
        request.session['pro_site_fi']=''
        site_status= None
    try:
        btwob = request.session['pro_btw_fi']
    except:
        request.session['pro_btw_fi']=''
        btwob=None
    try:
        ware_status = request.session['pro_ware_fi']
    except:
        request.session['pro_ware_fi']=''
        ware_status=None

    if 'filter_s' in  request.POST:
        category = request.POST.getlist('category')
        category_site = request.POST.getlist('category_site')
        vendor = request.POST.getlist('vendor')
        site_status = request.POST.get('site_status')
        ware_status = request.POST.get('ware_status')
        if category_site:
            request.session['pro_cat_site'] = category_site
            products = products.filter(category_site__title__in=category_site)
        else:
            request.session['pro_cat_site'] = None

        if category:
            request.session['pro_cat_fi'] = category
            products=products.filter(category__title__in=category)
        else:
            request.session['pro_cat_fi'] = None

        if vendor:
            request.session['pro_ven_fi']=vendor
            products=products.filter(supplier__title__in=vendor)
        else:
            request.session['pro_ven_fi'] = None
        if site_status:
            request.session['pro_site_fi'] = site_status
            if site_status == 'a':
                products = products.filter(status=True)
            if site_status == 'i':
                products = products.filter(status=False)
        else:
            request.session['pro_site_fi'] = None
        if ware_status:
            if ware_status == 'a':
                products = products.filter(ware_active=True)
            if ware_status == 'b':
                products = products.filter(ware_active=False)
            request.session['pro_ware_fi'] = ware_status

        else:
            request.session['pro_ware_fi'] = None

        btwob = request.POST.get('btwob_status')
        if btwob:
            request.session['pro_btw_fi'] = btwob
            products = products.filter(carousel=btwob)
        else:
            request.session['pro_btw_fi'] = None
    try:
        if category:
            products = products.filter(category__title__in=category)
    except:
        pass

    try:
        if vendor:
            products = products.filter(supplier__title__in=vendor)
    except:
        pass
    try:
        if ware_status:
            products = products.filter(ware_active = ware_status)
    except:
        pass
    if 'search_pro' in request.POST:
        query =request.POST.get('search_pro')
        if query:
            products = products.filter(
                Q(title__contains=query)|
                Q(category__title__contains=query) |
                Q(supplier__title__contains=query) |
                Q(order_code__icontains=query)
            ).distinct()
        try:
            if category:
                products = products.filter(category__title__in=category)
        except:
                pass
        try:
            if vendor:
                products = products.filter(supplier__title__in=vendor)
        except:
            pass
        try:
            if ware_status:
                products = products.filter(ware_active = ware_status)
        except:
            pass
    if 'table_form' in request.POST:
        form = ToolsTableOrderForm(request.POST,instance=table_control_order)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = ToolsTableOrderForm(instance=table_control_order)
    try:
        products = products.order_by('%s'%(table_control_order.table_order_by))
    except:
        pass
    paginator = Paginator(products, table_control_order.show_number_of_products)
    page = request.GET.get('page')
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        product = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        product = paginator.page(paginator.num_pages)
    if 'product_button' in request.POST:
        choosed_products = request.POST.getlist('choose_product')
        print(choosed_products)
        activate = request.POST.get('action')
        request.session['choosed_products'] = choosed_products
        request.session['product_action'] = activate
        return HttpResponseRedirect('/αποθήκη/εργαλεία/product-checkbox-options/')
    context ={
        'currency':currency,
        #check filters
        'category_name':category,
        'vendor_name':vendor,
        'site_status_name':site_status,
        'ware_status_name':ware_status,
        'btwob_name':btwob,
        'products':product,
        'title':title,
        'categories':categories,
        'categories_sites':categories_site,
        'vendors':vendors,
        'tools_table':table_control_order,
        'form':form,
    }
    context.update(csrf(request))
    return render(request, 'inventory/products_edit_section_NEW.html',context)

@staff_member_required()
def ajax_product_search(request):
    if request.POST:
        search_text = request.POST['search_text']
    else:
        search_text = ''
    if len(search_text) <= 2:
        return render_to_response('ajax/ware_product_search.html',{'my_products':None,})
    else:
        products = Product.objects.filter(
                                        Q(title__contains=search_text) |
                                        Q(category__title__contains=search_text )|
                                        Q(supplier__title__contains=search_text) |
                                        Q(order_code__icontains=search_text)|
                                        Q(sku__contains=search_text)
                                        ).distinct()
        return render_to_response('ajax/ware_product_search.html',{'my_products':products,})

@staff_member_required()
def product_checkbox_options(request):
    products = request.session['choosed_products']
    action = request.session['product_action']
    if action == 'activate':
        for dk in products:
            product = Product.objects.get(id=dk)
            product.ware_active = 'a'
            product.save()
    elif action == 'deactivate':
         for dk in products:
            product = Product.objects.get(id=dk)
            product.ware_active = 'b'
            product.save()
    elif action == 'change_category':
        if request.POST:
            form = ChangeCategoryForm(request.POST)
            if form.is_valid():
                for dk in products:
                    product = Product.objects.get(id=dk)
                    product.category = Category.objects.get(id=request.POST['title'])
                    product.save()
                return HttpResponseRedirect('/αποθήκη/προιόντα/')
        else:
            form = ChangeCategoryForm()

        context = {
            'form':form,
        }
        context.update(csrf(request))
        return render_to_response('inventory/change_category_action.html',context)
    elif action=='change_vendor':
         if request.POST:
             form = ChangeVendorForm(request.POST)
             if form.is_valid():
                 for dk in products:
                     product = Product.objects.get(id=dk)
                     product.supplier = Supply.objects.get(id=request.POST['title'])
                     product.save()
                 return HttpResponseRedirect('/αποθήκη/προιόντα/')
         else:
             form = ChangeVendorForm()

         context= {
             'form':form,
         }
         context.update(csrf(request))
         return render_to_response('inventory/change_category_action.html',context)
    elif action == 'activate_site':
        for dk in products:
            product = Product.objects.get(id=dk)
            if product.status:
                product.status = False
            else:
                product.status = True
            product.save()
    else:
        pass

    #clear sessions
    request.session['choosed_products'] = None
    request.session['product_action'] = None
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required()
def create_duplicated_product(request,dk):
    product = Product.objects.get(id=dk)
    switch='edit'
    product_characteristics = ProductCharacteristics.my_query.filter(product_related=product)
    product_images = ProductPhotos.objects.filter(product=product)
    new_product = Product.objects.get(id=dk)
    new_product.id = None
    if request.POST:
        form = ProductForm(request.POST,request.FILES, instance=new_product, initial={'qty':0})
        if form.is_valid():
            form.save()
            color = form.cleaned_data.get('color')
            size = form.cleaned_data.get('size')
            saved_product = Product.objects.last()
            for char in product_characteristics:
                new_char = ProductCharacteristics.objects.create(title=char.title,
                                                                 description=char.description,
                                                                 content_type=ContentType.objects.get_for_model(Product),
                                                                 object_id=saved_product.id,
                                                                 )
                new_char.save()
            messages.success(request, 'Το προϊόν %s επεξεργάστηκε.'%(product.title))
            return HttpResponseRedirect('/αποθήκη/προιόντα/')
    else:
        form = ProductForm(instance=new_product, initial={'qty':0,})

    title ='Αντιγραφή %s' %(product.title)
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/create_product.html', context)

@staff_member_required()
def create_product(request):
    switch = 'new_product'
    if request.POST:
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            print('works')
            new_product = form.save()
            title  = form.cleaned_data.get('title')
            messages.success(request, 'Δημιουργήθηκε το Προϊόν...  %s' %(title))
            return redirect('edit_product', dk=new_product.id)

    else:
        try:
            form = ProductForm(initial={'title':request.session['create_pro_title'],
                                        'category':Category.objects.get(id=request.session['create_pro_cate']),
                                        'supplier':Supply.objects.get(id=request.session['create_pro_ven']),
                                        'size':request.session['create_pro_size'],
                                        'color':request.session['create_pro_color'],
                                        'notes':request.session['create_pro_notes']})
        except:
            form = ProductForm()


    context = {
        'title': 'Δημιουργία Προϊόντος',
        'form':form,
        'switch':switch,
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_product.html', context)

@staff_member_required()
def product_add_characteristics(request,dk):
    product = get_object_or_404(Product,id=dk)
    if request.POST:
        form = ProductCharacteristicsForm(request.POST,initial={'product_related':product})
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/αποθήκη/προιόντα/επεξεργασία/%s/'%(dk))
    else:
        form = ProductCharacteristicsForm(initial={'product_related':product})

    context={
        'form':form,
        'title':'Add Characteristic',
        'return_page':'/αποθήκη/προιόντα/επεξεργασία/%s/'%(dk),
    }
    context.update(csrf(request))
    return render(request,'inventory/create_costumer_form.html', context)

@staff_member_required()
def create_brand(request, dk=None):
    if request.POST:
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if dk:
                return HttpResponseRedirect('/αποθήκη/προιόντα/επεξεργασία/%s/'%(dk))
            return HttpResponseRedirect('/αποθήκη/προιόντα/δημιουργία/')
    else:
        form = BrandForm()
    title='Δημιουργία Brand'
    if dk:
        return_page = '/αποθήκη/προιόντα/επεξεργασία/%s/' %(dk)
    else:
        return_page ='/αποθήκη/προιόντα/δημιουργία/'
    context={
        'form':form,
        'title':title,
        'return_page':return_page
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def create_category_site_from_product(request, dk=None):
    if request.POST:
        form =CategorySiteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if dk:
                return HttpResponseRedirect('/αποθήκη/προιόντα/επεξεργασία/%s/'%(dk))
            return HttpResponseRedirect('/αποθήκη/προιόντα/δημιουργία/')
    else:
        form = CategorySiteForm()
    title='Δημιουργία Κατηγορίας Site'
    if dk:
        return_page = '/αποθήκη/προιόντα/επεξεργασία/%s/' %(dk)
    else:
        return_page ='/αποθήκη/προιόντα/δημιουργία/'
    context={
        'form':form,
        'title':title,
        'return_page':return_page
    }

    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def create_vendor_from_product(request):
    form_vendor = VendorForm(request.POST)
    if form_vendor.is_valid():
        form_vendor.save()
        messages.success(request, 'Ο Προμηθευτής προστέθηκε.')
        return HttpResponseRedirect('/αποθήκη/προιόντα/δημιουργία/')
    else:
        form_vendor = VendorForm()
    context = {
        'return_page': '/αποθήκη/προιόντα/δημιουργία/',
        'title':'Νέος Προμηθευτής',
        'form':form_vendor,
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def create_category_from_product(request):
    form_vendor = CategoryForm(request.POST)
    if form_vendor.is_valid():
        form_vendor.save()
        messages.success(request, 'H Κατηγορία προστέθηκε.')
        return HttpResponseRedirect('/αποθήκη/προιόντα/δημιουργία/')
    else:
        form_vendor =CategoryForm()
    context = {
        'return_page': '/αποθήκη/προιόντα/δημιουργία/',
        'title':'Νέα Κατηγορία',
        'form':form_vendor,
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def edit_product(request, dk):
    switch='edit'
    product = Product.objects.get(id=dk)
    product_characteristics = ProductCharacteristics.my_query.filter(content_type= ContentType.objects.get_for_model(Product), object_id=product.id)
    product_images = product.get_all_images()
    product_sizes = SizeAttribute.objects.filter(product_related=product)
    related_products = RelatedProducts.objects.filter(title=product).last()
    product_colors = SameColorProducts.objects.filter(title=product).last()
    if 'related_pro' in request.POST:
        related_item = request.POST.get('related_pro')
        print(related_item)
    if request.POST:
        form = ProductForm(request.POST,request.FILES, instance=product)
        if form.is_valid():
            form.save()
            color = form.cleaned_data.get('color')
            size = form.cleaned_data.get('size')
            if size == 'a':
                return HttpResponseRedirect('/αποθήκη/προιόντα/δημιουργία/add_color/%s'%(dk))
            elif color == 'a':
                return HttpResponseRedirect('/αποθήκη/προιόντα/δημιουργία/add_only_color/%s'%(dk))
            else:
                messages.success(request, 'Το προϊόν %s επεξεργάστηκε.'%(product.title))
                return HttpResponseRedirect('/αποθήκη/προιόντα/')
    else:
        form = ProductForm(instance=product)
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/create_product.html', context)

@staff_member_required()
def ajax_related_products(request):
    if request.POST:
        search_text = request.POST.get('search_text')
        dk = request.POST.get('dk')
    else:
        search_text = ''
        dk=1
    if len(search_text) <= 2:
        return render_to_response('ajax/ware_product_search.html',{'my_products':None,})
    else:
        products = Product.objects.filter(
                                        Q(title__contains=search_text)|
                                        Q(category__title__contains=search_text)|
                                        Q(supplier__title__contains=search_text)|
                                        Q(order_code__icontains=search_text)
                                        ).distinct()
        return render_to_response('ajax/ware_product_search.html',{'my_products':products,
                                                                   'related_pro':True,
                                                                   'dk':dk,
                                                                   })

@staff_member_required()
def add_or_remove_related_products(request, dk, pk):
    product = Product.objects.get(id=dk)
    add_related = Product.objects.get(id=pk)
    exists = RelatedProducts.objects.filter(title=product)
    if exists:
        print('exists')
        related_product = RelatedProducts.objects.get(title=product)
        related_product.related.add(add_related)
        related_product.save()
    else:
        print('new')
        related_product = RelatedProducts.objects.create(title=product)
        related_product.save()
        related_product.related.add(add_related)
        related_product.save()

    return redirect('edit_product', dk=dk)

@staff_member_required()
def delete_related_product(request, dk, pk):
    related_product = Product.objects.get(id=dk)
    product_model = RelatedProducts.objects.get(id=pk)
    product_model.related.remove(related_product)
    product_model.save()
    messages.success(request, 'Το προτεινόμενο προϊόν διαγράφηκε.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required()
def ajax_color_products(request):
    if request.POST:
        search_text = request.POST.get('search_tet')
        dk = request.POST.get('dk_')
    else:
        search_text = ''
        dk=1
    if len(search_text) <= 2:
        return render_to_response('ajax/ware_product_search.html',{'my_products':None,})
    else:
        products = Product.objects.filter(
                                        Q(title__contains=search_text)|
                                        Q(category__title__contains=search_text)|
                                        Q(supplier__title__contains=search_text)|
                                        Q(order_code__icontains=search_text)
                                        ).distinct()
        return render_to_response('ajax/ware_product_search.html',{'my_products':products,
                                                                   'color_pro':True,
                                                                   'dk':dk,
                                                                   })

@staff_member_required()
def add_or_remove_color_products(request, dk, pk):
    product = Product.objects.get(id=dk)
    add_related = Product.objects.get(id=pk)
    exists = SameColorProducts.objects.filter(title=product)
    if exists:
        related_product = SameColorProducts.objects.get(title=product)
        related_product.related.add(add_related)
        related_product.save()
    else:
        related_product = SameColorProducts.objects.create(title=product)
        related_product.save()
        related_product.related.add(add_related)
        related_product.save()
    return redirect('edit_product', dk=dk)

@staff_member_required()
def delete_color_product(request, dk, pk):
    related_product = Product.objects.get(id=dk)
    product_model = SameColorProducts.objects.get(id=pk)
    product_model.related.remove(related_product)
    product_model.save()
    messages.success(request, 'Το προτεινόμενο προϊόν διαγράφηκε.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required()
def edit_product_create_size(request, dk):
    add_size= True #template switch
    product = Product.objects.get(id=dk)
    get_product_sizes = SizeAttribute.objects.filter(product_related=product)
    title = product.title
    sizes = Size.objects.all()

    if request.POST:
        get_sizes = request.POST.getlist('get_sizes')
        for size in get_sizes:
            exists = get_product_sizes.filter(title__id = int(size))
            if not exists:
                new_size = SizeAttribute.objects.create(title = Size.objects.get(id=int(size)), product_related= product)
                new_size.save()
        return redirect('edit_product', dk=dk)
    context= locals()
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def edit_product_edit_number(request, dk):
    size = SizeAttribute.objects.get(id=dk)
    title = '%s - %s'%(size.product_related, size.title)
    image = size.product_related.image
    if request.POST:
        form = SizeAttributeForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.update_product(sizeAttr=size)
            messages.success(request, 'Η ποσότητα ανανεώθηκε.')
            return redirect('edit_product', dk=size.product_related.id)
    else:
        form = SizeAttributeForm(initial={'title':size.title, 'qty':size.qty})
    return_page = size.product_related.absolute_url_edit_product()
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def edit_product_delete_number(request, dk):
    size = SizeAttribute.objects.get(id=dk)
    size.delete_update_product()
    size.delete()
    messages.warning(request, 'Το νούμερο %s διαγράφηκε.'%(size.title))
    return redirect('edit_product', dk=size.product_related.id)

@staff_member_required()
def add_photo_to_product(request, dk):
    product = Product.objects.get(id=dk)
    if request.POST:
        form = CreatePhoto(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Η φωτογραφία προστέθηκε.')
            return redirect('edit_product', dk=dk)
    else:
        form = CreatePhoto(initial={'product':product,})
    context ={
        'form':form,
        'return_page':http_referer(request),
        'title':'Επιλογή Φωτογραφίας.'
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def delete_photo_from_product(request, dk):
    photo = ProductPhotos.objects.get(id=dk)
    product = photo.product
    photo.delete()
    messages.warning(request, 'Η φωτογραφία διαγράφηκε.')
    return redirect('edit_product', dk=product.id)

@staff_member_required()
def edit_photo_from_product(request,dk):
    photo = ProductPhotos.objects.get(id=dk)
    if request.POST:
        form = CreatePhoto(request.POST,request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request,'Η φωτογραφία επεξεργάστηκε.')
            return redirect('edit_product', dk=photo.object_id)
    else:
        form = CreatePhoto(instance=photo)

    context ={
        'form':form,
        'return_page':request.META.get('HTTP_REFERER'),
        'title':'Επιλογή Φωτογραφίας.'
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def add_characteristic_from_product(request, dk, type):
    return_redirect = None
    content_type = None
    if type == 'product':
        content_type = ContentType.objects.get_for_model(Product)
        return_redirect = 'edit_product'
    if request.POST:
        form = ProductCharacteristicsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Προστέθηκε Χαρακτηριστικό')
            return redirect(return_redirect, dk=dk)
    else:
        form = ProductCharacteristicsForm(initial={'object_id':dk,
                                                   'content_type':content_type,
                                                   })
    context = {
        'title':'Προσθήκη Χρακτηριστικού',
        'return_page':http_referer(request),
        'form':form
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def delete_char_from_product(request,dk):
    char = ProductCharacteristics.objects.get(id=dk)
    char.delete()
    messages.warning(request, 'Το χαρακτηριστικό διαγράφηκε.')
    return redirect('edit_product', dk=char.object_id)

@staff_member_required()
def edit_char_from_product(request, dk, pk):
    char = ProductCharacteristics.objects.get(id=dk)
    if request.POST:
        form = ProductCharacteristicsForm(request.POST, instance=char)
        if form.is_valid():
            form.save()
            messages.success(request, 'To Χαρακτηριστικό επεξεργάστηκε.')
            return redirect('edit_product', dk=pk)
    else:
        form = ProductCharacteristicsForm(instance=char)
    context = {
        'title':'Επεξεργασία Χαρακτηριστικού',
        'return_page':http_referer(request),
        'form':form
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def edit_char_from_color_attr(request, dk, pk):
    char = ProductCharacteristics.objects.get(id=dk)
    if request.POST:
        form = ProductCharacteristicsForm(request.POST, instance=char)
        if form.is_valid():
            form.save()
            messages.success(request, 'To Χαρακτηριστικό επεξεργάστηκε.')
            return redirect('edit_color_attr', dk=pk)
    else:
        form = ProductCharacteristicsForm(instance=char)
    context = {
        'title':'Επεξεργασία Χρακτηριστικού',
        'return_page':http_referer(request),
        'form':form
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required()
def delete_size(request, dk, pk):
    size = SizeAttribute.objects.get(id=pk)
    size.delete()
    return HttpResponseRedirect('/αποθήκη/προιόντα/δημιουργία/add_color/%s/'%(dk))

@staff_member_required()
def activate_deactivate_product(request, dk):
    product = Product.objects.get(id =dk)
    if product.ware_active == True:
        product.ware_active = False
        product.save()
        messages.success(request, 'Το προϊόν %s απενεργοποιήθηκε'%(product.title) )
        return HttpResponseRedirect('/αποθήκη/προιόντα/')
    else:
        product.ware_active = True
        product.save()
        messages.success(request, 'Το προϊόν %s ενεργοποιήθηκε'%(product.title) )
        return HttpResponseRedirect('/αποθήκη/προιόντα/')

def delete_relatives(instance, product,):
    try:
        check = instance.objects.filter(product_related=product)
    except:
        check = instance.objects.filter(related=product)
    if check:
        for ele in check:
            ele.delete()

def delete_product(request, dk,):
    product =get_object_or_404(Product, id=dk)
    order_item_exists = OrderItem.objects.filter(product=product)
    retail_item_exists = RetailOrderItem.objects.filter(title=product)
    if order_item_exists or retail_item_exists:
        messages.warning(request, 'Το προϊόν έχει ήδη χρισημοποιηθεί σε τιμολόγιο ή πώληση')
        return HttpResponseRedirect('/αποθήκη/προιόντα/')
    checks_photos = ProductPhotos.objects.filter(product=product)
    if checks_photos:
        for photo in checks_photos:
            photo.delete()
    delete_relatives(SizeAttribute, product)
    delete_relatives(ProductCharacteristics, product)
    delete_relatives(RelatedProducts, product)
    delete_relatives(SameColorProducts, product)
    product.delete()
    messages.warning(request, 'Το προϊόν διαγράφηκε!')
    return HttpResponseRedirect('/αποθήκη/προιόντα/')

