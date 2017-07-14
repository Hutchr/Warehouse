from django.shortcuts import render, HttpResponseRedirect,get_object_or_404 ,render_to_response
from django.template.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages

from PoS.models import Shipping, PaymentMethod, Order_status, RetailOrderItem, RetailOrder
from products.models import *
from .models import *
from account.models import CostumerAccount
from cart.models import CartItem, CartRules
from blog.models import Post, PostCategory, PostTags
from .models import Footer, SiteSettings, OfferPage

from cart.views import card_id, add_to_cart_check_size
from account.forms import RegisterForm, CostumerProfileForm
from .forms import CheckoutForm, WelcomePageForm, FooterForm, SiteSettingsForm, NewsLetterForm
from PoS.forms import RetailForm
import random
from account.forms import CostumerPageEditDetailsForm
from comment.forms import CommentForm
from .tools import *
from blog.forms import PostCreate, PostTagForm, PostCategoryForm
from comment.models import Comment, CommentType
from dateutil.relativedelta import relativedelta
from itertools import chain

ORDER_NUMBERS = [10,20,50,100]
def get_initial_page_data(request):
    welcome_page = WelcomePage.objects.filter(active=True).last()
    categories = CategorySite.my_query.main_page_show()
    offer = OfferPage.objects.filter(active=True, page_related=welcome_page).last()
    banners = Banners.objects.filter(active=True, page_related=welcome_page)
    front_messages = FrontPageMessages.objects.filter(is_active=True, page_related=welcome_page)
    second_banners = SecondSectionBanners.objects.filter(active=True, page_related=welcome_page)
    footer = Footer.objects.filter(active=True, page_related=welcome_page).last()
    footer_cat = FooterCategory.objects.filter(footer=footer)
    user_terms = UserTerms.objects.filter(related_to=welcome_page)
    try:
        cart_id = card_id(request)
        cart_items = CartItem.my_query.current_session_and_active(cart_id=cart_id)
    except:
        cart_items = None
    return [welcome_page, categories, offer, banners, front_messages, second_banners, footer, footer_cat, user_terms, cart_items]

def site_filters(request, products):
    products = products
    initial_categories, initial_brands,initial_sizes,initial_colors=[[],[],[],[]]
    for product in products:
        if not product.brand in initial_brands and product.brand:
            initial_brands.append(product.brand)
        if not product.color in initial_colors and product.color:
            initial_colors.append(product.color)
        if not product.category_site in initial_categories and product.category_site:
            initial_categories.append(product.category_site)
        if product.have_size():
            for size__attr in product.sizeattribute_set.all():
                if size__attr.title not in initial_sizes:
                    initial_sizes.append(size__attr.title)
    get_categories, get_colors,get_sizes,get_brands = [[],[],[],[]]
    if request.GET:
        get_brands = request.GET.getlist('brand_name')
        get_categories = request.GET.getlist('category_name')
        get_colors = request.GET.getlist('color_name')
        get_sizes = request.GET.getlist('size_name')
        if get_brands:
            products = products.filter(brand__id__in=get_brands)
        if get_categories:
            products = products.filter(category_site__id__in=get_categories)
        if get_colors:
            products = products.filter(color__id__in=get_colors)
        if get_sizes:
            get_products_sizes = SizeAttribute.objects.filter(title__id__in=get_sizes, product_related__in=products)
            get_products_colors=[]
            for size in get_products_sizes:
                get_products_colors.append(size.product_related.id)
            products = products.filter(id__in= get_products_colors)
    return [[initial_categories, initial_brands,initial_sizes,initial_colors, products],[get_brands, get_categories, get_colors, get_sizes]]

def ordering_and_pagination(request, products):
    show_products, order_by = 10, 'price'
    if request.GET:
        show_products = request.GET.get('show_product') if request.GET.get('show_product') else 10
        order_by = request.GET.get('sort-by') if request.GET.get('sort_by') else 'price'
    try:
        products = products.order_by('%s'%order_by)
    except:
         products, order_by = products.order_by('price'), 'price'
    try:
        show_products_exists = isinstance(int(show_products),int)
        # checks if the get request for pagination show items is integer.
        # If it is pass the number else pass the default of 10 items
    except:
        show_products = 10
    return products, show_products, order_by

#@cache_page(60*15)
def homepage(request):
    currency = CURRENCY
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    eshop_identity = CompanyInfo.objects.get(id=1)
    last_products = Product.my_query.active_for_site()[:20]
    brands = Brands.objects.all()
    posts = Post.objects.all()
    if 'register_post' in request.POST:
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        register_form = RegisterForm()
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    if 'newsletter' in request.POST:
        newsletter_form = NewsLetterForm(request.POST)
        if newsletter_form.is_valid():
            newsletter_form.save()
            messages.success(request, 'Το email σας καταχωρήθηκε!')
            return HttpResponseRedirect('/')
    else:
        newsletter_form = NewsLetterForm()
    if request.POST:
        username= request.POST.get('email-modal')
        password = request.POST.get('password-modal')
        user = auth.authenticate(username=username,password=password)
        if user:
            auth.login(request,user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = locals()
    context.update(csrf(request))
    return render(request, 'obaju/index.html',context)

#@cache_page(60*15)
def product_page(request, slug):
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    eshop_identity = CompanyInfo.objects.get(id=1)
    product = get_object_or_404(Product, slug=slug)
    check_if_new = datetime.datetime.now().date() - product.day_added
    check_new = False
    if check_if_new.days <30:
        check_new= True
    try:
        product_colors = SameColorProducts.objects.filter(title=product).last().related.all()
    except:
        product_colors= None
    try:
       related_products = RelatedProducts.objects.filter(title=product).last().related.all()
    except:
        related_products = None
    more_images = product.get_all_images()[0:1]
    product_char = ProductCharacteristics.my_query.filter(content_type= ContentType.objects.get_for_model(Product), object_id=product.id)
    vendor_products = Product.my_query.active_with_qty().filter(brand=product.brand).exclude(id=product.id).order_by('id')[0:3]
    category_products = Product.my_query.active_with_qty().filter(category_site=product.category_site).exclude(id=product.id).order_by('id')[0:3]
    characteristics = ProductCharacteristics.my_query.filter_by_instance(product)
    add_to_cart_check_size(request, product=product)
    currency = CURRENCY
    context = locals()
    context.update(csrf(request))
    return render(request,'obaju/detail.html', context)

def new_items_page(request):
    products = Product.objects.all().order_by('-id')[0:30]
    pass
#@cache_page(60*15)

def offers_product_page(request):
    offers = True #template_tag switcher!
    order_numbers = ORDER_NUMBERS
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    products = Product.my_query.site_offers()
    initial_categories, initial_brands,initial_sizes,initial_colors, products = site_filters(request, products=products)[0]
    get_brands, get_categories, get_colors, get_sizes = site_filters(request, products=products)[1]
    products, show_products, order_by = ordering_and_pagination(request, products=products)
    paginator = Paginator(products, show_products) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    context = locals()
    context.update(csrf(request))
    return render_to_response('obaju/category.html',context)

#@cache_page(60*15)
def page_results(request):
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    eshop_identity = CompanyInfo.objects.get(id=1)
    search_text = request.GET.get('search_pro')
    products = Product.my_query.active_for_site().filter(
                                        Q(title__contains=search_text)|
                                        Q(category__title__contains=search_text)|
                                        Q(supplier__title__contains=search_text)|
                                        Q(sku__icontains=search_text)
                                      ).distinct()
    initial_categories, initial_brands,initial_sizes,initial_colors, products = site_filters(request, products=products)[0]
    get_brands, get_categories, get_colors, get_sizes = site_filters(request, products=products)[1]
    products, show_products, order_by = ordering_and_pagination(request, products=products)
    paginator = Paginator(products, show_products) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    context = locals()
    context.update(csrf(request))
    return render_to_response('obaju/category.html',context)

def ajax_results(request):
    if request.POST:
        search_text = request.POST['search_text']
        print(search_text)
    else:
        search_text = ''
    if len(search_text) <= 2:
        return render_to_response('ajax/ware_product_search.html',{'my_products':None,})
    else:
        products = Product.my_query.active_with_qty().filter(
                                        Q(title__contains=search_text)|
                                        Q(category__title__contains=search_text)|
                                        Q(supplier__title__contains=search_text)|
                                        Q(sku__icontains=search_text)
                                        ).distinct()
        return render_to_response('ajax/ware_product_search.html',{'my_products':products,'my_site':True,})

#@cache_page(60*15)
def category_site(request, slug):
    order_numbers = ORDER_NUMBERS
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    eshop_identity = CompanyInfo.objects.get(id=1)
    #get the initial data of the page-------------------------------------------------------------------------------
    category_site = CategorySite.objects.get(slug=slug)
    get_all_categories = []
    for category in category_site.categorysite_set.all():
        if not category in get_all_categories:
            get_all_categories.append(category)
            for cat in category.categorysite_set.all():
                if cat not in get_all_categories:
                    get_all_categories.append(cat)
    if not get_all_categories:
        products = Product.my_query.active_get_one_category_site(category=category_site)
    else:
        products = Product.my_query.active_get_all_category_site(list_of_category=get_all_categories)
    initial_categories, initial_brands,initial_sizes,initial_colors, products = site_filters(request, products=products)[0]
    get_brands, get_categories, get_colors, get_sizes = site_filters(request, products=products)[1]
    products, show_products, order_by = ordering_and_pagination(request, products=products)
    paginator = Paginator(products, show_products) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    context = locals()
    context.update(csrf(request))
    return render(request, 'obaju/category.html', context)

#@cache_page(60*15)
def brand_page_products(request, slug):
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    eshop_identity = CompanyInfo.objects.get(id=1)
    #get the initial data of the page-------------------------------------------------------------------------------
    brand = Brands.objects.get(slug=slug)
    products = Product.my_query.active_with_brand(brand=brand.id)
    initial_categories, initial_brands,initial_sizes,initial_colors, products = site_filters(request, products=products)[0]
    get_brands, get_categories, get_colors, get_sizes = site_filters(request, products=products)[1]
    products, show_products, order_by = ordering_and_pagination(request, products=products)
    paginator = Paginator(products, show_products) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    context=locals()
    context.update(csrf(request))
    return render_to_response('obaju/category.html',context)

def cart_html(request):
    try:
        cart_items = CartItem.current_session(cart_id=request.session['cart_id'])
    except:
        cart_items = []
    return render_to_response('obaju/cart_item.html',{'cart_items':cart_items,
                                                      'test':2})

def change_show_product_number(request, dk):
    request.session['show_product'] = dk
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#gonna get removed
def my_site_clear_session(request,slug):
    if slug == 'get_brands':
        request.session['get_brands'] = None
    elif slug == 'get_categories':
        request.session['get_categories'] = None
    elif slug == 'get_color':
        request.session['get_color'] = None
    else:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def basket(request):
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    rules = CartRules.objects.get(id=1)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    eshop_identity = CompanyInfo.objects.get(id=1)
    related_products = []
    total_price = 0
    total_qty = 0
    for item in cart_items:
        related_products.append(RelatedProducts.objects.get(title=item.product).related.all())
        if item.size:
            total_price += item.price()
        else:
            total_price += item.price() * item.qty
            total_qty += item.qty
    if len(related_products) < 3:
        related_products = Product.my_query.active_with_qty()[:5]
    if 'change_qty' in request.POST:
        for item in cart_items:
            new_qty = request.POST.get('%s'%item.id)
            if int(new_qty) > item.product.qty:
                messages.warning(request,'Το προιόν δεν έχει %s επαρκεί ποσότητα.'%(item.product.title))
            else:
                item.qty = int(new_qty)
                item.save()
    currency = CURRENCY
    context = locals()
    return render(request, 'obaju/basket.html', context)

def checkout(request):
    try:
        cart_items = CartItem.my_query.current_session_and_active(cart_id=card_id(request))
    except:
        cart_items= None
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    shipping = Shipping.my_query.active_and_site()
    payment_method = PaymentMethod.my_query.active_and_site()
    if request.user.is_authenticated():
        costumer_account = CostumerAccount.objects.get(user=request.user)
        if request.POST:
            form = CheckoutForm(request.POST, initial={'first_name':costumer_account.first_name,
                                             'last_name':costumer_account.last_name,
                                             'city':costumer_account.shipping_city,
                                             'address':costumer_account.shipping_address_1,
                                             'state':costumer_account.shipping_city,
                                             'zip':costumer_account.shipping_zip_code,
                                             'cell_phone':costumer_account.cellphone,
                                             'phone':costumer_account.phone,
                                             'email':request.user.email,
                                             })
            if form.is_valid():
                shipping_id = request.POST.get('delivery')
                shipping_id = int(shipping_id)
                payment_id = request.POST.get('payment')
                payment_id = int(payment_id)
                if form.is_valid():
                    new_order = RetailOrder.objects.create(notes=request.POST.get('notes') or None,
                                                            order_type='e',
                                                            status=Order_status.objects.get(id=1),
                                                            eshop_order_id=generate_eshop_order_id(),
                                                            eshop_session_id=card_id(request),
                                                            shipping=Shipping.objects.get(id=shipping_id),
                                                            payment_method=PaymentMethod.objects.get(id=payment_id),
                                                            costumer_account=costumer_account,
                                                            first_name=request.POST.get('first_name'),
                                                            last_name=request.POST.get('last_name'),
                                                            city=request.POST.get('city'),
                                                            state=request.POST.get('state'),
                                                            zip_code=request.POST.get('zip'),
                                                            cellphone=request.POST.get('cell_phone'),
                                                            phone=request.POST.get('phone'),
                                                            email=request.POST.get('email'),
                                                            )
                    new_order.save()
                    for cart_item in cart_items:
                        cart_item.active = False
                        cart_item.is_ordered= True
                        cart_item.save()
                        cart_item.eshop_confirm_order()
                        new_order_item = RetailOrderItem.objects.create(order=new_order,
                                                                             title=cart_item.product,
                                                                             cost=cart_item.product.price_buy,
                                                                             price=cart_item.product.site_price,
                                                                             qty=cart_item.qty,
                                                                        )
                        if cart_item.size:
                            new_order_item.size = cart_item.size
                        new_order_item.save()
                        new_order.value += cart_item.product.site_price * cart_item.qty
                        new_order.total_cost += cart_item.product.price_buy * cart_item.qty
                        new_order.save()
                        new_order.costumer_account.balance += new_order.value
                        new_order.costumer_account.save()
                return HttpResponseRedirect('/checkout-review/')
        else:
            form = CheckoutForm(initial={'first_name':costumer_account.first_name,
                                             'last_name':costumer_account.last_name,
                                             'city':costumer_account.shipping_city,
                                             'address':costumer_account.shipping_address_1,
                                             'state':costumer_account.shipping_city,
                                             'zip':costumer_account.shipping_zip_code,
                                             'cell_phone':costumer_account.cellphone,
                                             'phone':costumer_account.phone,
                                             'email':request.user.email
                                             })


    else:
        if request.POST:
            form = CheckoutForm(request.POST)
            if form.is_valid():
                shipping_id = request.POST.get('delivery')
                shipping_id = int(shipping_id)
                payment_id = request.POST.get('payment')
                payment_id = int(payment_id)
                if form.is_valid():
                    new_order = RetailOrder.objects.create(
                                                             notes = request.POST.get('notes') or None,
                                                             order_type = 'e',
                                                             status = Order_status.objects.get(id=1),
                                                             eshop_order_id = generate_eshop_order_id(),
                                                             eshop_session_id = card_id(request),
                                                             first_name= request.POST.get('first_name'),
                                                             last_name = request.POST.get('last_name'),
                                                             city = request.POST.get('city'),
                                                             address = request.POST.get('address'),
                                                             state = request.POST.get('state')or None,
                                                             zip_code = request.POST.get('zip'),
                                                             cellphone = request.POST.get('cell_phone'),
                                                             phone = request.POST.get('phone') or None,
                                                             email = request.POST.get('email') or None,
                                                             shipping = Shipping.objects.get(id=shipping_id),
                                                             payment_method = PaymentMethod.objects.get(id=payment_id),
                                                             costumer_account = CostumerAccount.objects.get(id = 1),
                                                             )
                    new_order.save()
                    for cart_item in cart_items:
                        cart_item.active = False
                        cart_item.is_ordered= True
                        cart_item.save()
                        cart_item.eshop_confirm_order()
                        new_order_item = RetailOrderItem.objects.create(order = new_order,
                                                                         title = cart_item.product,
                                                                         cost = cart_item.product.price_buy,
                                                                         price = cart_item.product.site_price,
                                                                         qty = cart_item.qty,

                        )
                        if cart_item.size:
                            new_order_item.size = cart_item.size
                        new_order_item.save()
                        new_order.value += cart_item.product.site_price * cart_item.qty
                        new_order.total_cost += cart_item.product.price_buy * cart_item.qty
                        new_order.costumer_account.balance += new_order.value
                        new_order.costumer_account.save()
                        new_order.save()
                return HttpResponseRedirect('/checkout-review/')
        else:
            form = CheckoutForm()
    try:
        cart_id = card_id(request)
        cart_items = CartItem.objects.filter(cart_id=cart_id)
    except:
        cart_items = None
    context ={
        'cart_items':cart_items,
        'categories':categories,
        'welcome_page':welcome_page,
        'form':form,
        'shipping':shipping,
        'payment_method':payment_method,
    }
    context.update(csrf(request))
    return render(request, 'obaju/checkout1.html', context)

def checkout_review(request):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    try:
        order = RetailOrder.objects.filter(eshop_session_id=card_id(request)).last()
        order_items = RetailOrderItem.objects.filter(order=order)
    except:
        order = None
        order_items = None
    try:
        cart_id = card_id(request)
        cart_items = CartItem.my_query.current_session_and_active(cart_id=cart_id)
    except:
        cart_items = None
    context ={
        'cart_items':cart_items,
        'order_items':order_items,
        'categories':categories,
        'welcome_page':welcome_page,
        'order':order,
    }
    return render(request, 'obaju/checkout4.html', context)

@login_required
def my_account(request):
    #it will be removed
    user = request.user
    context = {

    }
    return render(request,'my_site/my_account.html', context)

def register_page(request):
    welcome_page = WelcomePage.objects.get(id=1)
    if 'login' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request,user)
            return HttpResponseRedirect('/')
    if 'register' in request.POST:
        print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if username and password and email and first_name and last_name:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            create_costumer_account = CostumerAccount.objects.create(user=user,
                                                                     first_name=first_name,
                                                                     last_name=last_name,
                                                                     )
            create_costumer_account.save()
            user = auth.authenticate(username=username, password= password)
            auth.login(request,user)
            return redirect('costumer_page')
    context= {
        'welcome_page':welcome_page,

    }
    context.update(csrf(request))
    return render_to_response('obaju/register.html', context)

@login_required
def costumer_page(request):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    if 'search_pro' in request.POST:
        search_text = request.POST['search_pro']
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    try:
        cart_id = card_id(request)
        cart_items = CartItem.my_query.current_session_and_active(cart_id=cart_id)
    except:
        cart_items = None
    user = request.user
    costumer_account = CostumerAccount.objects.get(user=user)
    if 'details' in request.POST:
        costumer_details = CostumerPageEditDetailsForm(request.POST, instance=costumer_account)
        if costumer_details.is_valid():
            costumer_details.save()
            return HttpResponseRedirect('/costumer-page')
    else:
        costumer_details = CostumerPageEditDetailsForm(instance=costumer_account)
    if 'pass_form' in request.POST:
        password_form = ''
        pass
    context={
        'categories':categories,
        'welcome_page':welcome_page,
        'cart_items':cart_items,
        'costumer_account':costumer_account,
        'costumer_details':costumer_details,
    }

    return render(request, 'obaju/customer-account.html',context)

@login_required
def costumer_ask_page(request):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    costumer = CostumerAccount.objects.get(user = request.user)
    content_type  = costumer.get_content_type
    object_id = costumer.id
    if 'search_pro' in request.POST:
        search_text = request.POST['search_pro']
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    try:
        cart_id = card_id(request)
        cart_items = CartItem.my_query.current_session_and_active(cart_id=cart_id)
    except:
        cart_items = None
    if 'add_msg' in request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            get_data = form.cleaned_data.get('content')
            new_comment = Comment.objects.create(user = request.user,
                                                 content_type = content_type,
                                                 object_id =object_id,
                                                 comment_type = CommentType.objects.get(id=1),
                                                 content = get_data
                                                 )
            new_comment.save()
            messages.success(request, 'its done')
            return redirect(reverse('costumer_ask_page'))
    else:
        form = CommentForm(initial={'user':request.user,
                                    'comment_type':CommentType.objects.get(id=1),
                                    })

    context={
        'categories':categories,
        'welcome_page':welcome_page,
        'cart_items':cart_items,
        'form':form
    }
    context.update(csrf(request))
    return render(request, 'obaju/customer-wishlist.html', context)

@login_required
def costumer_page_order(request):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    if 'search_pro' in request.POST:
        search_text = request.POST['search_pro']
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))

    try:
        cart_id = card_id(request)
        cart_items = CartItem.my_query.current_session_and_active(cart_id=cart_id)
    except:
        cart_items = None
    user = request.user
    costumer_account = CostumerAccount.objects.get(user=user)
    orders = RetailOrder.objects.filter(costumer_account=costumer_account).order_by('-day_added')

    context={
        'categories':categories,
        'welcome_page':welcome_page,
        'cart_items':cart_items,
        'costumer_account':costumer_account,
        'orders':orders,

    }

    return render(request, 'obaju/customer-orders.html',context)

def costumer_specific_order(request, order_id):
    welcome_page = WelcomePage.objects.get(id=1)
    order = get_object_or_404(RetailOrder, eshop_order_id=order_id)
    order_items = order.lianikiorderitem_set.all()
    context={
        'welcome_page':welcome_page,
        'order':order,
        'order_items':order_items,
    }
    return render(request, 'obaju/customer-order.html', context)
from newsletter.forms import ContactForm

def contact_page(request):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    eshop_info = EshopInformation.objects.get(id=1)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    if 'contact_form' in request.POST:
        form = ContactForm(request.POST, initial={'date_created':datetime.datetime.now()})
        if form.is_valid():
            form.save()
            messages.success(request, 'Ευχαριστούμε για το μήνυμα μας, θα επικοινωνοίσουμε μαζί σας το συντομότερο δυνατόν')
            return redirect('contact_page')
    else:
        form = ContactForm
    context = locals()
    context.update(csrf(request))
    return render(request, 'obaju/contact.html', context)

def faq_page(request):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    questions = EshopAskQuestions.objects.filter(status=True)
    context={
        'categories':categories,
        'welcome_page':welcome_page,
        'questions':questions,
    }
    return render(request, 'obaju/faq.html', context)

def informations_page(request):
    welcome_page, categories, offer, banners, front_page_messages, second_banners, footer, footer_cat, user_terms, cart_items = get_initial_page_data(request)
    if 'search_pro' in request.POST:
        search_text = request.POST.get('search_pro')
        return redirect(reverse('page_results') + '?search_pro=%s'%(search_text))
    eshop_identity = CompanyInfo.objects.get(id=1)
    info_data = EshopInformation.objects.last()
    gallery = Gallery.objects.all()
    context = locals()
    return render(request, 'obaju/text.html', context)

def generate_eshop_order_id():
    cart_id=''
    characters = 'ABCDEFGHIJKLMNOPQRQSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 10
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id


#-------------------------------------Site admin--------------------------------------------------
