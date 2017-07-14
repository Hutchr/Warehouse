from django.shortcuts import render, HttpResponseRedirect,get_object_or_404 ,render_to_response
from django.template.context_processors import csrf
from products.models import *
from .models import WelcomePage, Banners, SecondSectionBanners, UserTerms, FrontPageMessages, EshopAskQuestions, EshopInformation, CompanyInfo
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from blog.models import Post, PostCategory, PostTags
from .models import Footer, SiteSettings, OfferPage
from .forms import WelcomePageForm, FooterForm, SiteSettingsForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages
from PoS.models import Shipping, PaymentMethod,  Order_status, RetailOrderItem, RetailOrder
from PoS.forms import RetailForm, EshopEditForm
from django.db.models import Q
import random
from account.forms import CostumerPageEditDetailsForm
from comment.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from .tools import *
from products.views import CURRENCY
from blog.forms import PostCreate, PostTagForm, PostCategoryForm
from comment.models import Comment, CommentType
from dateutil.relativedelta import relativedelta
from itertools import chain




@staff_member_required
def print_order(request, dk):
    order = RetailOrder.objects.get(id = dk)
    order_items = order.retailorderitem_set.all()
    site_info = CompanyInfo.objects.last()
    return_page = request.META.get('HTTP_REFERER')
    return render_to_response('print_statements/print_order_for_site.html',{'order':order,
                                  'order_items':order_items,
                                  'return_page':return_page,
                                  'site_info':site_info,
    })

@staff_member_required
def site_admin(request):
    today = datetime.datetime.now()
    yesterday = today - relativedelta(days=1)
    new_eshop_orders = RetailOrder.my_query.eshop_new_orders()
    new_eshop_items = RetailOrderItem.objects.filter(order__in=new_eshop_orders)
    sent_eshop_orders = RetailOrder.my_query.eshop_done_orders(date_start=yesterday, date_end=today)
    context={
        'new_eshop_orders':new_eshop_orders,
        'new_eshop_items':new_eshop_items,
        'sent_eshop_orders':sent_eshop_orders,
    }
    return render(request, 'my_site/index.html',context)


@staff_member_required
def site_show_messages(request):
    messages_ = Comment.objects.all()
    new_messages = messages_.filter(stuff_readed = False)
    return render_to_response('my_site/site_msg_section.html',{"messages":messages_,
                                                               'new_messages':new_messages,})

@staff_member_required
def site_blog(request):
    all_posts = Post.objects.all()
    post_category = PostCategory.objects.all()
    post_tags = PostTags.objects.all()
    context={
        'all_posts':all_posts,
        'post_categories':post_category,
        'post_tags':post_tags,
    }
    return render(request, 'my_site/blog/blog_admin.html',context)

@staff_member_required
def site_blog_create_cat(request):
    if request.POST:
        form = PostCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_admin')
    else:
        form = PostCategoryForm()

    context={
        'title':'Καινούργια Κατηγορία',
        'form':form,
        'return_page':request.META.get('HTTP_REFERER')
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html' ,context)

@staff_member_required
def site_blog_edit(request, dk):
    post = get_object_or_404(Post, id=dk)
    if request.POST:
        form = PostCreate(request.POST,request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/site/blog/')
    else:
        form = PostCreate(instance=post)
    context={
        'form':form,
    }
    context.update(csrf(request))
    return render(request,'my_site/blog/create_blog.html', context)

@staff_member_required
def site_blog_edit_cat(request, dk):
    tag = get_object_or_404(PostCategory, id=dk)
    if request.POST:
        form = PostCategoryForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('blog_admin')
    else:
        form = PostCategoryForm(instance=tag)

    context={
        'title':tag.title,
        'form':form,
        'return_page':request.META.get('HTTP_REFERER')
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html', context)

@staff_member_required
def site_blog_create_tag(request):
    if request.POST:
        form = PostTagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_admin')
    else:
        form = PostTagForm()

    context={
        'title':'Καινούργια Κατηγορία',
        'form':form,
        'return_page':request.META.get('HTTP_REFERER')
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html' ,context)

@staff_member_required
def site_blog_edit_tag(request, dk):
    tag = get_object_or_404(PostTags, id=dk)
    if request.POST:
        form = PostTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('blog_admin')
    else:
        form = PostTagForm(instance=tag)

    context={
        'title':tag.title,
        'form':form,
        'return_page':request.META.get('HTTP_REFERER')
    }
    context.update(csrf(request))
    return render_to_response('inventory/create_costumer_form.html', context)

@staff_member_required
def orders_management(request):
    date_end = datetime.datetime.today()
    date_start = date_end - relativedelta(month=1)
    get_current_shipping = request.session.get('shipping_order_admin')
    get_current_payment =request.session.get('payment_order_admin')
    orders = RetailOrder.my_query.eshop_orders().filter(day_created__range=[date_start,date_end])
    shipping = Shipping.objects.all()
    payment_method = PaymentMethod.objects.all()
    payment_id = None
    shipping_id = None
    if request.GET:
        shipping_id = request.GET.getlist('shipping')
        payment_id = request.GET.getlist('payment_name')
        search_text = request.GET.get('search_text')
        orders = orders.filter(Q(title__icontains =search_text)|
                               Q(first_name__icontains=search_text)|
                               Q(last_name__icontains=search_text)|
                               Q(address__icontains=search_text)|
                               Q(zip_code__icontains=search_text)|
                               Q(cellphone__icontains=search_text)|
                               Q(phone__icontains=search_text)).distinct()
        if shipping_id:
            orders =orders.filter(shipping__id__in=shipping_id)
        if payment_id:
            orders = orders.filter(payment_method__id__in=payment_id)
    else:
        if not get_current_shipping == None:
            orders = orders.filter(shipping__id__in =get_current_shipping)
        if not get_current_payment == None:
            orders = orders.filter(payment_method__id__in=get_current_payment)

    context = {
        'orders':orders,
        'title':'Όλες οι Παραγγελίες',
        'shipping':shipping,
        'payment_method':payment_method,
        'payment_name':payment_id,
        'shipping_name':shipping_id,
    }
    context.update(csrf(request))
    return render(request, 'my_site/order_management.html', context)

@login_required
def new_eshop_orders(request):
    get_current_shipping = request.session.get('shipping_order_admin')
    get_current_payment =request.session.get('payment_order_admin')
    orders = RetailOrder.my_query.eshop_new_orders()
    shipping = Shipping.objects.all()
    payment_method = PaymentMethod.objects.all()
    payment_id = None
    shipping_id = None
    if request.GET:
        shipping_id = request.GET.getlist('shipping')
        payment_id = request.GET.getlist('payment_name')
        search_text = request.GET.get('search_text')
        orders = orders.filter(Q(title__icontains =search_text)|
                               Q(first_name__icontains=search_text)|
                               Q(last_name__icontains=search_text)|
                               Q(address__icontains=search_text)|
                               Q(zip_code__icontains=search_text)|
                               Q(cellphone__icontains=search_text)|
                               Q(phone__icontains=search_text)).distinct()
        if shipping_id:
            orders =orders.filter(shipping__id__in=shipping_id)
        if payment_id:
            orders = orders.filter(payment_method__id__in=payment_id)
    else:
        if not get_current_shipping == None:
            orders = orders.filter(shipping__id__in =get_current_shipping)
        if not get_current_payment == None:
            orders = orders.filter(payment_method__id__in=get_current_payment)
    context = {
        'orders':orders,
        'title':'Νέες Παραγγελίες',
        'shipping':shipping,
        'payment_method':payment_method,
        'payment_name':payment_id,
        'shipping_name':shipping_id,
    }
    context.update(csrf(request))
    return render(request, 'my_site/order_management.html', context)

def in_progress_eshop_orders(request):
    get_current_shipping = request.session.get('shipping_order_admin')
    get_current_payment =request.session.get('payment_order_admin')
    orders = RetailOrder.my_query.eshop_orders_on_progress()
    shipping = Shipping.objects.all()
    payment_method = PaymentMethod.objects.all()
    payment_id = None
    shipping_id = None
    if request.GET:
        shipping_id = request.GET.getlist('shipping')
        payment_id = request.GET.getlist('payment_name')
        search_text = request.GET.get('search_text')
        orders = orders.filter(Q(title__icontains =search_text)|
                               Q(first_name__icontains=search_text)|
                               Q(last_name__icontains=search_text)|
                               Q(address__icontains=search_text)|
                               Q(zip_code__icontains=search_text)|
                               Q(cellphone__icontains=search_text)|
                               Q(phone__icontains=search_text)).distinct()
        if shipping_id:
            orders =orders.filter(shipping__id__in=shipping_id)
        if payment_id:
            orders = orders.filter(payment_method__id__in=payment_id)
    else:
        if not get_current_shipping == None:
            orders = orders.filter(shipping__id__in =get_current_shipping)
        if not get_current_payment == None:
            orders = orders.filter(payment_method__id__in=get_current_payment)
    context = {
        'orders':orders,
        'title':'Παραγγελίες σε Εξέλιξη',
        'shipping':shipping,
        'payment_method':payment_method,
        'shipping_name':shipping_id,
        'payment_name':payment_id
    }
    context.update(csrf(request))
    return render(request, 'my_site/order_management.html', context)

@login_required
def done_eshop_orders(request):
    get_current_shipping = request.session.get('shipping_order_admin')
    get_current_payment =request.session.get('payment_order_admin')
    orders = RetailOrder.my_query.eshop_orders().filter(status__id__in=[6,7])
    shipping = Shipping.objects.all()
    payment_method = PaymentMethod.objects.all()
    if request.POST:
        shipping_id = request.POST.getlist('shipping')
        payment_id = request.POST.getlist('payment_name')
        search_text = request.POST.get('search_text')
        orders = orders.filter(Q(title__icontains =search_text)|
                               Q(first_name__icontains=search_text)|
                               Q(last_name__icontains=search_text)|
                               Q(address__icontains=search_text)|
                               Q(zip_code__icontains=search_text)|
                               Q(cellphone__icontains=search_text)|
                               Q(phone__icontains=search_text)).distinct()
        if shipping_id:
            orders =orders.filter(shipping__id__in=shipping_id)
            request.session['shipping_order_admin'] = [int(x) for x in shipping_id]

        if payment_id:
            orders = orders.filter(payment_method__id__in=payment_id)
            request.session['payment_order_admin'] =payment_id
    else:
        if not get_current_shipping == None:
            orders = orders.filter(shipping__id__in =get_current_shipping)
        if not get_current_payment == None:
            orders = orders.filter(payment_method__id__in=get_current_payment)
    context = {
        'orders':orders,
        'title':'Ολοκληρωμένες',
        'shipping':shipping,
        'payment_method':payment_method,
    }
    context.update(csrf(request))
    return render(request, 'my_site/order_management.html', context)

@login_required
def products_in_progress(request):
    orders = RetailOrder.my_query.eshop_orders_in_warehouse()
    order_items = RetailOrderItem.objects.filter(order__in=orders).order_by('-order__status__id')
    return render_to_response('my_site/order_management.html', {'order_items':order_items,
                                                                'title':'Ροή Προιόντων',
                                                                'products':True
                                                                })

@staff_member_required
def eshop_order(request,dk):
    order = RetailOrder.objects.get(id=dk)
    order_items = RetailOrderItem.objects.filter(order=order)
    order_status = Order_status.objects.all()
    shipping = Shipping.my_query.active_and_site()
    payment_method = PaymentMethod.objects.all()
    currency = CURRENCY
    context = locals()
    return render(request, 'my_site/eshop_order.html', context)

@staff_member_required
def eshop_order_full_edit(request, dk):
    eshop_order = RetailOrder.objects.get(id=dk)
    if request.POST:
        form = EshopEditForm(request.POST, instance=eshop_order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Η παραγγελία %s επεξεργάστηκε επιτυχώς.' %(eshop_order.title) )
            return redirect('eshop_order',dk=dk )
    else:
        form = EshopEditForm(instance=eshop_order)
    context = {
        'title':eshop_order.title,
        'form':form,
        'return_page':request.META.get('HTTP_REFERER')
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)

@staff_member_required
def order_item_is_find(request, dk, pk):
    order_item = RetailOrderItem.objects.get(id=dk)
    order = order_item.order
    if order_item.is_find:
        order_item.is_find =False
        order_item.save()
    else:
        order_item.is_find = True
        order_item.save()
    if order.status.id == 1:
        order.status = Order_status.objects.get(id=2)
        order.save()
    return HttpResponseRedirect('/site/order_management/order/%s'%(order.id))

@staff_member_required
def eshop_change_status(request, dk, pk):
    order = get_object_or_404(RetailOrder, id=dk)
    change_order_status(lianiki_order=order, old_id=order.status.id, new_id=pk)
    order.status = Order_status.objects.get(id=pk)
    order.save()
    return HttpResponseRedirect('/site/order_management/order/%s'%(dk))

@staff_member_required
def eshop_change_shipping(request,dk,pk):
    order = get_object_or_404(RetailOrder, id=dk)
    order.shipping = Shipping.objects.get(id=pk)
    order.save()
    return HttpResponseRedirect('/site/order_management/order/%s'%(dk))

@staff_member_required
def eshop_change_payment(request,dk,pk):
    order = get_object_or_404(RetailOrder, id=dk)
    order.payment_method = PaymentMethod.objects.get(id=pk)
    order.save()
    return HttpResponseRedirect('/site/order_management/order/%s'%(dk))

@staff_member_required
def eshop_change_order_item(request, dk):
    order_item = RetailOrder.objects.get(id=dk)
    order = order_item.order
    if request.POST:
        pass

@login_required
def eshop_edit_order(request, dk):
    order = get_object_or_404(RetailOrder, id=dk)
    if request.POST:
        form = EshopOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('ehop_order', dk=dk)
    else:
        form = EshopOrderForm(instance=order)

    context = {
        'title':order.title,
        'form':form,
        'return_page':request.META.get('HTTP_REFERER')
    }
    return render_to_response('inventory/create_costumer_form.html', context)


@login_required
def site_blog_create(request):
    if request.POST:
        form = PostCreate(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/site/blog/')
    else:
        form = PostCreate()
    context={
        'form':form,
    }
    context.update(csrf(request))
    return render(request,'my_site/blog/create_blog.html', context)


def site_control(request):
    welcome_page = WelcomePage.objects.get(id=1)
    footer = Footer.objects.get(id=1)
    front_page_messages = FrontPageMessages.objects.all()
    site_settings = SiteSettings.objects.get(id=1)
    if 'welcome_page' in request.POST:
        welcome_page_form = WelcomePageForm(request.POST, instance=welcome_page)
        if welcome_page_form.is_valid():
            welcome_page_form.save()
            messages.success(request, 'Η επεξεργασία αποθηκεύτηκε.')
            return redirect('site_control')
    else:
        welcome_page_form= WelcomePageForm(instance=welcome_page)

    if 'footer' in request.POST:
        footer_form = FooterForm(request.POST, instance=footer)
        if footer_form.is_valid():
            footer_form.save()
            messages.success(request, 'Η επεξεργασία αποθηκεύτηκε.')
            return redirect('site_control')
    else:
        footer_form = FooterForm(instance=footer)

    if 'site_settings' in request.POST:
        site_setting_form = SiteSettingsForm(request.POST, instance=site_settings)
        if site_setting_form.is_valid():
            site_setting_form.save()
            messages.success(request, 'Η επεξεργασία αποθηκεύτηκε.')
            return redirect('site_control')
    else:
        site_setting_form = SiteSettingsForm(instance=site_settings)


    context = {
        'welcome_page':welcome_page,
        'footer':footer,
        'front_page_messages':front_page_messages,
        'site_settings_form':site_setting_form,
        'welcome_page_form':welcome_page_form,
        'footer_form':footer_form,
    }
    context.update(csrf(request))
    return render(request, 'my_site/site_control.html', context)

def site_control_banners(request):
    banners = Banners.objects.all()
    second_banners = SecondSectionBanners.objects.all()

    context = {
        'banners':banners,
        'second_banners':second_banners
    }
    context.update(csrf(request))
    return render(request, 'my_site/site_control_banners.html', context)

def site_newsletter(request):
    newsletters_list = NewsLetter.objects.all()

    if request.POST:
        costumer_filter = request.POST.get('costumer')
        status_filter  = request.POST.get('status')
        if costumer_filter:
            newsletters_list = newsletters_list.exclude(user__isnull= True)
        if status_filter:
            newsletters_list = newsletters_list.filter(user_approve = True)

    paginator = Paginator(newsletters_list, 50)
    page = request.GET.get('page')
    try:
        newsletters = paginator.page(page)
    except PageNotAnInteger:
        newsletters = paginator.page(1)
    except EmptyPage:
        newsletters = paginator.page(paginator.num_pages)

    context = {
        'newsletters':newsletters,
    }
    context.update(csrf(request))
    return render_to_response('my_site/site_control_news_letter.html', context)

def site_contact_info(request):
    ask_questions = EshopAskQuestions.objects.all()
    eshop_info = EshopInformation.objects.get(id=1)
    user_terms = UserTerms.objects.get(id=1)
    company_info = CompanyInfo.objects.get(id=1)


    context = {
            'ask_questions':ask_questions,
            'eshop_info':eshop_info,
            'user_terms':user_terms,
            'company_info':company_info,

    }
    return render_to_response('my_site/site_control_contact.html', context)
