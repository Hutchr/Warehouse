from django.shortcuts import render, render_to_response, HttpResponseRedirect, redirect
from products.models import *
from inventory_manager.models import *
from PoS.models import *
from tools.views import ToolsTableOrder, reports_initial_date, date_pick_session, date_pick_form
from tools.forms import ToolsTableOrderForm
from django.db.models import Q, F
#from django.db.models.functions import TruncMonth
from django.db.models import ExpressionWrapper, DecimalField
from transcations.models import *
from django.db.models import Avg, Max, Min, Sum, Count
from products.utils import *
from account.models import CostumerAccount
from django.template.context_processors import csrf
from itertools import chain
from operator import attrgetter
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from inventory_manager.form import PreOrderItemForm
from django.contrib import messages
from PoS.models import *
from dateutil.relativedelta import relativedelta
import datetime
from tools.views import diff_month
MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

def initial_date(request, months=3):
    #gets the initial last three months or the session date
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range = date_range.split('-')
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')
        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
    except:
        date_three_months_ago = date_now - relativedelta(months=months)
        date_start = date_three_months_ago
        date_end = date_now
        date_range = None
        request.session['date_range'] = '%s - %s'%(str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]

def set_session(request):
    try:
        costumer_name = request.session['report_income_costu']
    except:
        request.session['report_income_costu']=None
        costumer_name = None
    try:
        order_type_name = request.session['report_income_type']
    except:
        request.session['report_income_type'] = None
        order_type_name =None
    try:
        shipping_name =request.session['report_income_ship']
    except:
        request.session['report_income_ship'] = None
        shipping_name = None
    try:
        date_pick = request.session['report_income_date']
    except:
        request.session['report_income_date'] = None
        date_pick=None

def reports_income(request):
    costumers = CostumerAccount.objects.all()
    shipping = Shipping.objects.all()
    payment_methods = PaymentMethod.objects.all()
    date_start, date_end, date_range = initial_date(request)
    set_session(request)
    # get the days between the selected dates and created another one date range on past
    days = date_end - date_start
    previous_period_start = date_start - relativedelta(days=days.days)
    previous_period_end = date_start - relativedelta(days=1)
    previous_period = '%s - %s'%(str(previous_period_end).split(' ')[0].replace('-','/'),str(previous_period_start).split(' ')[0].replace('-','/'))
    order_items_previous_period = RetailOrder.objects.filter(status__id =7, day_created__range =[previous_period_start, previous_period_end+relativedelta(days=1)]).order_by('-day_created')
    #creates last year date range
    last_year_start = date_start - relativedelta(years=1)
    last_year_end = date_end - relativedelta(years=1)
    orders_items_last_year = RetailOrder.objects.filter(status__id__in =[7, 8], day_created__range =[last_year_start, last_year_end]).order_by('-day_created')
    #gets the data from three months before
    orders = RetailOrder.objects.all().filter(day_created__range=[date_start, date_end], status__id__in =[7,8]).order_by('-day_created')
    costumer_name = None
    if request.POST:
        orders = RetailOrder.objects.all().filter(status__id__in=[7,8], day_created__range=[date_start, date_end]).order_by('-day_created')
        date_pick = request.POST.get('date_pick')
        costumer_name = request.POST.get('costumer_name')
        shipping_name = request.POST.get('shipping_name')
        if date_pick:
            try:
                date_range = date_pick.split('-')
                date_range[0]=date_range[0].replace(' ','')
                date_range[1]=date_range[1].replace(' ','')
                start_month =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                day_now =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
                orders = orders.filter(day_added__range=[start_month,day_now])
                request.session['report_income_date']=date_pick
            except:
                request.session['report_income_date'] = None
        if costumer_name:
            orders = orders.filter(costumer_account__id=costumer_name)
            request.session['report_income_costu'] = CostumerAccount.objects.get(id=costumer_name).full_name()
        if shipping_name:
            orders = orders.filter(shipping__title=shipping)
            request.session['report_income_ship'] = shipping_name
    # average values
    avg_cost = 0
    avg_profit = 0
    avg_income = 0
    if orders:
        avg_cost = orders.aggregate(Avg('total_cost'))['total_cost__avg']
        avg_income = orders.aggregate(Avg('paid_value'))['paid_value__avg']
        avg_profit = avg_income - avg_cost
    #analysis
    incomes_per_type = {}
    incomes_per_payment = {}
    incomes_per_costumer = {}
    total_stats = [0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0] #total incomes, taxes, clean_value, cost, quantity, current_date_range, previous, last year
    for order in orders:
        if order.order_type == 'r':
            total_stats[0], total_stats[1], total_stats[2], total_stats[3] = [total_stats[0]+order.paid_value, total_stats[1]+order.order_taxes(), total_stats[2]+ (order.paid_value - order.order_taxes()), total_stats[3]+order.total_cost]
            total_stats[4] = total_stats[4]+1 if order.status.id == 7 else total_stats[4]
            if order.order_type in incomes_per_type.keys():
                get_data = incomes_per_type[order.order_type]
                get_data[0], get_data[1], get_data[2], get_data[3], get_data[4] = [get_data[0]+order.paid_value, get_data[1]+order.order_taxes(), get_data[2]+order.order_clean_value(), get_data[3]+order.total_cost, get_data[4]+1]
                incomes_per_type[order.order_type] = get_data
            else:
                incomes_per_type[order.order_type] = [order.paid_value, order.order_taxes(), order.order_clean_value(), order.total_cost, 1, 0,0,0,0,0, 0,0,0,0,0]
            if order.costumer_account in incomes_per_costumer.keys():
                get_data = incomes_per_costumer[order.costumer_account]
                get_data[0], get_data[1], get_data[2], get_data[3], get_data[4] = [get_data[0]+order.paid_value, get_data[1]+order.order_taxes(), get_data[2]+order.order_clean_value(), get_data[3]+order.total_cost, get_data[4]+1]
                incomes_per_costumer[order.costumer_account] = get_data
            else:
                incomes_per_costumer[order.costumer_account] = [order.paid_value, order.order_taxes() , order.order_clean_value(), order.total_cost, 1, 0,0,0,0,1, 0,0,0,0,1]
            if order.payment_method in incomes_per_payment.keys():
                get_data = incomes_per_payment[order.payment_method]
                get_data[0], get_data[1], get_data[2], get_data[3], get_data[4] = [get_data[0]+order.paid_value, get_data[1]+order.order_taxes(), get_data[2]+order.order_clean_value(), get_data[3]+order.total_cost, get_data[4]+1]
                incomes_per_payment[order.payment_method] = get_data
            else:
                incomes_per_payment[order.payment_method] = [order.paid_value, order.order_taxes(), order.paid_value - order.order_taxes(), order.total_cost, 1, 0,0,0,0,1, 0,0,0,0,1]
        #check returns
        if order.order_type == 'b':
            total_stats[0], total_stats[1], total_stats[2], total_stats[3] = [total_stats[0]-order.paid_value, total_stats[1]-order.order_taxes(), total_stats[2]-(order.paid_value - order.order_taxes()), total_stats[3]-order.total_cost]
            if order.order_type in incomes_per_type.keys():
                get_data = incomes_per_type[order.order_type]
                get_data[0], get_data[1], get_data[2], get_data[3] = [get_data[0]-order.paid_value, get_data[1]-order.order_taxes(), get_data[2]-order.order_clean_value(), get_data[3]-order.total_cost]
                incomes_per_type[order.order_type] = get_data
            else:
                incomes_per_type[order.order_type] = [order.paid_value, order.order_taxes(), order.order_clean_value(), order.total_cost, 1, 0,0,0,0,0, 0,0,0,0,0 ]
            if order.costumer_account in incomes_per_costumer.keys():
                get_data = incomes_per_costumer[order.costumer_account]
                get_data[0], get_data[1], get_data[2], get_data[3] = [get_data[0]-order.paid_value, get_data[1]-order.order_taxes(), get_data[2]-order.order_clean_value(), get_data[3]-order.total_cost]
                incomes_per_costumer[order.costumer_account] = get_data
            else:
                incomes_per_costumer[order.costumer_account] = [order.paid_value, order.order_taxes() , order.order_clean_value(), order.total_cost, 1, 0,0,0,0,1, 0,0,0,0,1 ]
            if order.payment_method in incomes_per_payment.keys():
                get_data = incomes_per_payment[order.payment_method]
                get_data[0], get_data[1], get_data[2], get_data[3] = [get_data[0]-order.paid_value, get_data[1]-order.order_taxes(), get_data[2]-order.order_clean_value(), get_data[3]-order.total_cost]
                incomes_per_payment[order.payment_method] = get_data
            else:
                incomes_per_payment[order.payment_method] = [-order.paid_value, -order.order_taxes(), -(order.paid_value - order.order_taxes()), -order.total_cost, 1, 0,0,0,0,1, 0,0,0,0,1]

    #previous date_range
    for order in order_items_previous_period:
        if order.order_type == 'r':
            total_stats[5], total_stats[6], total_stats[7], total_stats[8] = [total_stats[5]+order.paid_value, total_stats[6]+order.order_taxes(), total_stats[7]+(order.paid_value - order.order_taxes()), total_stats[8]+order.total_cost]
            total_stats[9] = total_stats[9]+1 if order.status.id == 7 else total_stats[9]
            if order.order_type in incomes_per_type.keys():
                get_data = incomes_per_type[order.order_type]
                get_data[5], get_data[6], get_data[7], get_data[8], get_data[9] = [get_data[5]+order.paid_value, get_data[6]+order.order_taxes(), get_data[7]+order.order_clean_value(), get_data[8]+order.total_cost, get_data[9]+1]
                incomes_per_type[order.order_type] = get_data
            else:
                incomes_per_type[order.order_type] = [0,0,0,0,0, order.paid_value, order.order_taxes(), order.paid_value - order.order_taxes(), order.total_cost, 1, 0,0,0,0,0 ]
            if order.costumer_account in incomes_per_costumer.keys():
                get_data = incomes_per_costumer[order.costumer_account]
                get_data[5], get_data[6], get_data[7], get_data[8], get_data[9] = [get_data[5]+order.paid_value, get_data[6]+order.order_taxes(), get_data[7]+order.order_clean_value(), get_data[8]+order.total_cost, get_data[9]+1]
                incomes_per_costumer[order.costumer_account] = get_data
            else:
                incomes_per_costumer[order.costumer_account] = [0,0,0,0,0, order.paid_value, order.order_taxes(), order.paid_value - order.order_taxes(), order.total_cost, 1,  0,0,0,0,0 ]
            if order.payment_method in incomes_per_payment.keys():
                get_data = incomes_per_payment[order.payment_method]
                get_data[5], get_data[6], get_data[7], get_data[8], get_data[9] = [get_data[5]+order.paid_value, get_data[6]+order.order_taxes(), get_data[7]+order.order_clean_value(), get_data[8]+order.total_cost, get_data[9]+1]
                incomes_per_payment[order.payment_method] = get_data
            else:
                incomes_per_payment[order.payment_method] = [0,0,0,0,0, order.paid_value, order.order_taxes(), order.paid_value - order.order_taxes(), order.total_cost, 1, 0,0,0,0,0]

        #check returns previous date range
        if order.order_type == 'b':
            total_stats[5], total_stats[6], total_stats[7], total_stats[8] = [total_stats[5]-order.paid_value, total_stats[6]-order.order_taxes(), total_stats[7]-(order.paid_value - order.order_taxes()), total_stats[8]-order.total_cost]
            if order.order_type in incomes_per_type.keys():
                get_data = incomes_per_type[order.order_type]
                get_data[5], get_data[6], get_data[7], get_data[8] = [get_data[5]-order.paid_value, get_data[6]-order.order_taxes(), get_data[7]-order.order_clean_value(), get_data[8]-order.total_cost]
                incomes_per_type[order.order_type] = get_data
            else:
                incomes_per_type[order.order_type] = [order.paid_value, order.order_taxes(), order.order_clean_value(), order.total_cost, 1, 0,0,0,0,0, 0,0,0,0,0]
            if order.costumer_account in incomes_per_costumer.keys():
                get_data = incomes_per_costumer[order.costumer_account]
                get_data[5], get_data[6], get_data[7], get_data[8] = [get_data[5]-order.paid_value, get_data[6]-order.order_taxes(), get_data[7]-order.order_clean_value(), get_data[8]-order.total_cost]
                incomes_per_costumer[order.costumer_account] = get_data
            else:
                incomes_per_costumer[order.costumer_account] = [order.paid_value, order.order_taxes() , order.order_clean_value(), order.total_cost, 1, 0,0,0,0,1, 0,0,0,0,1 ]
            if order.payment_method in incomes_per_payment.keys():
                get_data = incomes_per_payment[order.payment_method]
                get_data[5], get_data[6], get_data[7], get_data[8] = [get_data[5]-order.paid_value, get_data[6]-order.order_taxes(), get_data[7]-order.order_clean_value(), get_data[8]-order.total_cost]
                incomes_per_payment[order.payment_method] = get_data
            else:
                incomes_per_payment[order.payment_method] = [0,0,0,0,0,-order.paid_value, -order.order_taxes(), -(order.paid_value - order.order_taxes()), -order.total_cost,  1, 0,0,0,0,0]

    #last year
    for order in orders_items_last_year:
        if order.order_type == 'r':
            total_stats[10], total_stats[11], total_stats[12], total_stats[13] = [total_stats[10]+order.paid_value, total_stats[11]+order.order_taxes(), total_stats[12]+(order.paid_value - order.order_taxes()), total_stats[13]+order.total_cost]
            total_stats[14] = total_stats[14]+1 if order.status.id == 7 else total_stats[14]
            if order.order_type in incomes_per_type.keys():
                get_data = incomes_per_type[order.order_type]
                get_data[10], get_data[11], get_data[12], get_data[13], get_data[14] = [get_data[10]+order.paid_value, get_data[11]+order.order_taxes(), get_data[12]+order.order_clean_value(), get_data[13]+order.total_cost, get_data[14]+1]
                incomes_per_type[order.order_type] = get_data
            else:
                incomes_per_type[order.order_type] = [0,0,0,0,0, 0,0,0,0,0,order.paid_value, order.order_taxes(), order.paid_value - order.order_taxes(), order.total_cost, 1 ]
            if order.costumer_account in incomes_per_costumer.keys():
                get_data = incomes_per_costumer[order.costumer_account]
                get_data[10], get_data[11], get_data[12], get_data[13], get_data[14] = [get_data[10]+order.paid_value, get_data[11]+order.order_taxes(), get_data[12]+order.order_clean_value(), get_data[13]+order.total_cost, get_data[14]+1]

                incomes_per_costumer[order.costumer_account] = get_data
            else:
                incomes_per_costumer[order.costumer_account] = [0,0,0,0,0, 0,0,0,0,0, order.paid_value, order.order_taxes(), order.paid_value - order.order_taxes(), order.total_cost, 1]
            if order.payment_method in incomes_per_payment.keys():
                get_data = incomes_per_payment[order.payment_method]
                get_data[10], get_data[11], get_data[12], get_data[13], get_data[14] = [get_data[10]+order.paid_value, get_data[11]+order.order_taxes(), get_data[12]+order.order_clean_value(), get_data[13]+order.total_cost, get_data[14]+1]
                incomes_per_payment[order.payment_method] = get_data
            else:
                incomes_per_payment[order.payment_method] = [0,0,0,0,0, 0,0,0,0,0, order.paid_value, order.order_taxes(), order.paid_value - order.order_taxes(), order.total_cost, 1]

        #check returns previous date range
        if order.order_type == 'b':
            total_stats[10], total_stats[11], total_stats[12], total_stats[13] = [total_stats[10]-order.paid_value, total_stats[11]-order.order_taxes(), total_stats[12]-(order.paid_value - order.order_taxes()), total_stats[13]-order.total_cost]
            if order.order_type in incomes_per_type.keys():
                get_data = incomes_per_type[order.order_type]
                get_data[10], get_data[11], get_data[12], get_data[13] = [get_data[10]-order.paid_value, get_data[11]-order.order_taxes(), get_data[12]-order.order_clean_value(), get_data[13]-order.total_cost]
                incomes_per_type[order.order_type] = get_data
            else:
                incomes_per_type[order.order_type] = [order.paid_value, order.order_taxes(), order.order_clean_value(), order.total_cost, 1, 0,0,0,0,0, 0,0,0,0,0]
            if order.costumer_account in incomes_per_costumer.keys():
                get_data = incomes_per_costumer[order.costumer_account]
                get_data[10], get_data[11], get_data[12], get_data[13] = [get_data[10]-order.paid_value, get_data[11]-order.order_taxes(), get_data[12]-order.order_clean_value(), get_data[13]-order.total_cost]
                incomes_per_costumer[order.costumer_account] = get_data
            else:
                incomes_per_costumer[order.costumer_account] = [order.paid_value, order.order_taxes() , order.order_clean_value(), order.total_cost, 1, 0,0,0,0,1, 0,0,0,0,1 ]
            if order.payment_method in incomes_per_payment.keys():
                get_data = incomes_per_payment[order.payment_method]
                get_data[10], get_data[11], get_data[12], get_data[13] = [get_data[10]-order.paid_value, get_data[11]-order.order_taxes(), get_data[12]-order.order_clean_value(), get_data[13]-order.total_cost]
                incomes_per_payment[order.payment_method] = get_data
            else:
                incomes_per_payment[order.payment_method] = [0,0,0,0,0, 0,0,0,0,0, -order.paid_value, -order.order_taxes(), -(order.paid_value - order.order_taxes()), order.total_cost, 1]
    title = 'Πωλήσεις'
    context = locals()
    context.update(csrf(request))
    return render(request, 'reports/incomes.html', context)

def reports_specific_order(request,dk):
    order = RetailOrder.objects.get(id=dk)
    order_items = order.retailorderitem_set.all()
    title = order.title
    context = {
        'title': title,
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'reports/income_specific_order.html', context)

def sell_items_flow(request):
    #create filters
    warehouse_categories = Category.objects.all()
    vendors= Supply.objects.all()
    site_categories = CategorySite.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()
    costumers = CostumerAccount.objects.all()
    date_start, date_end, date_range = initial_date(request)
    #initial start
    order_items = RetailOrderItem.objects.filter(order__day_created__range =[date_start, date_end]).order_by('-day_added')
    days = date_end - date_start
    previous_period_start = date_start - relativedelta(days=days.days)
    previous_period_end = date_start - relativedelta(days=1)
    previous_period = '%s - %s'%(str(previous_period_end).split(' ')[0].replace('-','/'),str(previous_period_start).split(' ')[0].replace('-','/'))
    order_items_previous_period = RetailOrderItem.objects.filter(order__day_created__range =[previous_period_start, previous_period_end+relativedelta(days=1)]).order_by('-day_added')
    last_year_start = date_start - relativedelta(years=1)
    last_year_end = date_end - relativedelta(years=1)
    orders_items_last_year = RetailOrderItem.objects.filter(order__day_created__range =[last_year_start,last_year_end]).order_by('-day_added')
    if 'filter_s' in request.POST:
        order_items = RetailOrderItem.objects.all()
        date_pick = request.POST.get('date_pick')
        category = request.POST.getlist('category')
        category_site = request.POST.getlist('category_site')
        vendor_name = request.POST.getlist('vendor')
        site_status = request.POST.get('site_status')
        ware_status = request.POST.get('ware_status')
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            start_month =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            day_now =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            order_items = RetailOrderItem.objects.filter(order__day_added__range=[start_month,day_now])
            days = date_end - date_start
            previous_period_start = date_start - relativedelta(days=days.days)
            previous_period_end = date_start - relativedelta(days=1)
            previous_period = '%s - %s'%(str(previous_period_end).split(' ')[0].replace('-','/'),str(previous_period_start).split(' ')[0].replace('-','/'))
            order_items_previous_period = RetailOrderItem.objects.filter(order__day_created__range =[previous_period_start, previous_period_end+relativedelta(days=1)]).order_by('-day_added')
            last_year_start = date_start - relativedelta(years=1)
            last_year_end = date_end - relativedelta(years=1)
            orders_items_last_year = RetailOrderItem.objects.filter(order__day_created__range =[last_year_start,last_year_end]).order_by('-day_added')
            request.session['date_range']=date_pick
        except:
            pass
        if vendor_name:
            request.session['pro_ven_fi']=vendor_name
            order_items = order_items.filter(title__supplier__title__in=vendor_name)
            order_items_previous_period = order_items_previous_period.filter(title__supplier__title__in=vendor_name)
            orders_items_last_year = orders_items_last_year.filter(title__supplier__title__in=vendor_name)
        else:
            request.session['pro_ven_fi'] = None
        if category_site:
            request.session['pro_cat_site'] = category_site
            order_items = order_items.filter(title__category_site__title__in=category_site)
            order_items_previous_period = order_items_previous_period.filter(title__category_site__title__in=category_site)
            orders_items_last_year = orders_items_last_year.filter(title__category_site__title__in=category_site)
        else:
            request.session['pro_cat_site'] = None
        if category:
            request.session['pro_cat_fi']=category
            order_items = order_items.filter(title__category__title__in = category)
            order_items_previous_period = order_items_previous_period.filter(title__category__title__in=category)
            orders_items_last_year = orders_items_last_year.filter(title__category__title__in=category)
        else:
            request.session['pro_cat_fi'] = None
        if site_status:
            request.session['pro_site_fi']=site_status
            order_items = order_items.filter(status__in=site_status)
            order_items_previous_period = order_items_previous_period.filter(status__in=site_status)
            orders_items_last_year = orders_items_last_year.filter(status__in=site_status)
        else:
            request.session['pro_site_fi'] = None
        if ware_status:
            request.session['pro_ware_fi']=ware_status
            order_items = order_items.filter(ware_active=ware_status)
            order_items_previous_period = order_items_previous_period.filter(ware_active=ware_status)
            orders_items_last_year = orders_items_last_year.filter(ware_active=ware_status)
        else:
            request.session['pro_ware_fi'] = None
        btwob = request.POST.get('btwob_status')
        if btwob:
            request.session['pro_btw_fi'] = btwob
            order_items = order_items.filter(carousel=btwob)
            orders_items_last_year = orders_items_last_year.filter(carousel=btwob)
            order_items_previous_period = order_items_previous_period.filter(carousel=btwob)
        else:
            request.session['pro_btw_fi'] = None

    # analysis
    total_report = [0,0,0,0] #incomes, cost, taxes, count
    ware_cate_report = {}
    vendors_report = {}
    costumers_report = {}

    for order in order_items:
        if order.order.order_type in ['r','e']:
            total_report[0], total_report[1], total_report[2],total_report[3] = [total_report[0] +order.total_price_number(), total_report[1]+order.total_cost(), total_report[2]+order.total_taxes(),total_report[3]+order.qty]
            if order.title.supplier in vendors_report.keys():
                #splits the information per vendor
                get_data = vendors_report[order.title.supplier]
                get_data[0], get_data[1], get_data[2], get_data[3] = [get_data[0]+order.total_price_number(), get_data[1]+order.total_cost(), get_data[2]+order.total_taxes(), get_data[3]+order.qty]
                vendors_report[order.title.supplier] = get_data
            else:
                vendors_report[order.title.supplier] = [order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0,0,0,0,0]
            if order.title.category in ware_cate_report.keys():
                get_data = ware_cate_report[order.title.category]
                ware_cate_report[order.title.category] = get_data
            else:
                ware_cate_report[order.title.category] = [order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0,0,0,0,0]
            if order.order.costumer_account in costumers_report.keys():
                get_data = costumers_report[order.order.costumer_account]
                get_data[0], get_data[1], get_data[2], get_data[3] = [get_data[0]+order.total_price_number(), get_data[1]+order.total_cost(), get_data[2]+order.total_taxes(), get_data[3]+order.qty]
                costumers_report[order.order.costumer_account] = get_data
            else:
                costumers_report[order.order.costumer_account] = [order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0,0,0,0,0]
    total_previous_period = [0,0,0,0]
    for order in order_items_previous_period:
        if order.order.order_type in ['e','r']:
            total_previous_period[0] += order.total_price_number()
            total_previous_period[1] += order.total_cost()
            total_previous_period[2] += order.total_taxes()
            total_previous_period[3] += order.qty
            if order.title.supplier in vendors_report.keys():
                get_data = vendors_report[order.title.supplier]
                get_data[4], get_data[5], get_data[6], get_data[7] = [get_data[4]+order.total_price_number(), get_data[5]+order.total_cost(), get_data[6]+order.total_taxes(), get_data[7]+order.qty]
                vendors_report[order.title.supplier] = get_data
            else:
                vendors_report[order.title.supplier] = [0,0,0,0,order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0]
            if order.title.category in ware_cate_report.keys():
                get_data = ware_cate_report[order.title.category]
                get_data[4], get_data[5], get_data[6], get_data[7] = [get_data[4]+order.total_price_number(), get_data[5]+order.total_cost(), get_data[6]+order.total_taxes(), get_data[7]+order.qty]
                ware_cate_report[order.title.category] = get_data
            else:
                ware_cate_report[order.title.category] = [0,0,0,0,order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0]
            if order.order.costumer_account in costumers_report.keys():
                get_data = costumers_report[order.order.costumer_account]
                get_data[4], get_data[5], get_data[6], get_data[7] = [get_data[4]+order.total_price_number(), get_data[5]+order.total_cost(), get_data[6]+order.total_taxes(), get_data[7]+order.qty]
                costumers_report[order.order.costumer_account] = get_data
            else:
                costumers_report[order.order.costumer_account] = [0,0,0,0,order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0]
        last_year_total = [0,0,0,0]
        for order in orders_items_last_year:
            last_year_total[0] += order.total_price_number()
            last_year_total[1] += order.total_cost()
            last_year_total[2] += order.total_taxes()
            last_year_total[3] += order.qty
            if order.title.supplier in vendors_report.keys():
                get_data = vendors_report[order.title.supplier]
                get_data[8], get_data[9], get_data[10], get_data[11] = [get_data[8]+order.total_price_number(), get_data[9]+order.total_cost(), get_data[10]+order.total_taxes(), get_data[11]+order.qty]
                vendors_report[order.title.supplier] = get_data
            else:
                vendors_report[order.title.supplier] = [0,0,0,0, 0,0,0,0, order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, ]
            if order.title.category in ware_cate_report.keys():
                get_data = ware_cate_report[order.title.category]
                get_data[8], get_data[9], get_data[10], get_data[11] = [get_data[8]+order.total_price_number(), get_data[9]+order.total_cost(), get_data[10]+order.total_taxes(), get_data[11]+order.qty]
                ware_cate_report[order.title.category] = get_data
            else:
                ware_cate_report[order.title.category] = [0,0,0,0, 0,0,0,0, order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, ]
            if order.order.costumer_account in costumers_report.keys():
                get_data = costumers_report[order.order.costumer_account]
                get_data[8], get_data[9], get_data[10], get_data[11] = [get_data[8]+order.total_price_number(), get_data[9]+order.total_cost(), get_data[10]+order.total_taxes(), get_data[11]+order.qty]
                costumers_report[order.order.costumer_account] = get_data
            else:
                costumers_report[order.order.costumer_account] = [0,0,0,0, 0,0,0,0, order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, ]
    title = 'Ροή Προϊόντων'
    context = {
        'title':title,
        'days':days,
        'previous_period':previous_period,
        'order_items':order_items,
        'warehouse_cate':warehouse_categories,
        'site_cate':site_categories,
        'vendors':vendors,
        'costumers':costumers,
        'profit': total_report[0]-total_report[1],
        'total_reports':total_report,
        'vendors_report':vendors_report,
        'ware_cate_report':ware_cate_report,
        'costumers_report':costumers_report,

    }
    context.update(csrf(request))
    return render(request, 'reports/order_item_flow.html', context)

def costumers_accounts_report(request):
    currency = CURRENCY
    title = 'Πελάτες'
    costumer_account = CostumerAccount.objects.all()
    search_text = request.POST.get('search_pro') or None
    if search_text:
        search_text = search_text
        costumer_account = costumer_account.filter(Q(first_name__icontains = search_text)|
                                                   Q(last_name__icontains = search_text)|
                                                   Q(user__email__icontains = search_text)|
                                                   Q(phone__icontains = search_text)|
                                                   Q(cellphone__icontains = search_text)
                                                   ).distinct()
    context = locals()
    context.update(csrf(request))
    return render_to_response('reports/costumer_account_report.html', context)

def specific_costumer_account(request, dk):
    costumer_account = CostumerAccount.objects.all()
    costumer_account_spe = CostumerAccount.objects.get(id=dk)
    orders = RetailOrder.objects.filter(costumer_account = costumer_account_spe)
    search_text = request.POST.get('search_pro') or None
    if search_text:
        search_text = search_text
        costumer_account = costumer_account.filter(Q(first_name__icontains = search_text)|
                                                   Q(last_name__icontains = search_text)|
                                                   Q(user__email__icontains = search_text)|
                                                   Q(phone__icontains = search_text)|
                                                   Q(cellphone__icontains = search_text)
                                                   ).distinct()

    context = locals()
    context.update(csrf(request))
    return render_to_response('reports/costumer_account_report.html', context)
#Isologismos

def isologismos(request):
    # creates the initial data for the default view
    day_now = datetime.datetime.now()
    start_year = datetime.datetime(datetime.datetime.now().year, 1,1)
    vendors = Supply.objects.all()
    categories = Category.objects.all()
    bills = Fixed_Costs_item.objects.all()
    occupations = Occupation.objects.all()
    #gets the total months of the year
    months_list = []
    month = 1
    months = diff_month(start_year,day_now)
    while month <= months+1:
        months_list.append(datetime.datetime(datetime.datetime.now().year, month, 1).month)
        month +=1
    #gets the data from the start of the year
    orders = RetailOrder.objects.all().filter(day_created__range=[start_year, day_now],order_type__in=['r', 'e'], status__id=7)
    return_orders = RetailOrder.objects.all().filter(day_created__range=[start_year, day_now], order_type='b')
    destroy_orders = DestroyOrder.objects.all().filter(day_added__range=[start_year,day_now])
    orders_b = Order.objects.all().filter(day_created__range=[start_year,day_now])
    log = Order_Fixed_Cost.objects.all().filter(date__range=[start_year,day_now])
    pagia_exoda =  Pagia_Exoda_Order.objects.all().filter(date__range=[start_year,day_now])
    people_pay = CreatePersonSalaryCost.objects.all().filter(day_expire__range=[start_year,day_now])
    pay_orders = PayOrders.objects.all().filter(date__range=[start_year,day_now])
    pay_log = PayOrderFixedCost.objects.all().filter(date__range=[start_year, day_now])
    person_pay = CreatePersonSalaryCost.objects.all().filter(day_added__range=[start_year, day_now],status ='b')
    pagia_exoda_pay = Pagia_Exoda_Pay_Order.objects.all().filter(day_added__range=[start_year, day_now])
    #filter section
    date_pick = None
    if request.POST:
        date_pick = request.POST.get('date_pick')
        if date_pick:
            if date_pick:
                try:
                    date_range = date_pick.split('-')
                    date_range[0]=date_range[0].replace(' ','')
                    date_range[1]=date_range[1].replace(' ','')
                    start_year =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                    day_now =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
                    orders = RetailOrder.objects.all().filter(day_added__range=[start_year,day_now])
                    orders_b = Order.objects.all().filter(date__range=[start_year,day_now])
                    log = Order_Fixed_Cost.objects.all().filter(date__range=[start_year,day_now])
                    pagia_exoda =  Pagia_Exoda_Order.objects.all().filter(date__range=[start_year,day_now])
                    people_pay = CreatePersonSalaryCost.objects.all().filter(day_expire__range=[start_year,day_now])
                    pay_orders = PayOrders.objects.all().filter(date__range=[start_year,day_now])
                    pay_log = PayOrderFixedCost.objects.all().filter(date__range=[start_year, day_now])
                    person_pay = CreatePersonSalaryCost.objects.all().filter(day_added__range=[start_year, day_now],status ='b')
                    pagia_exoda_pay = Pagia_Exoda_Pay_Order.objects.all().filter(day_added__range=[start_year, day_now])
                except:
                    date_pick = None
    #block right side
    #gets the actual paid from costumers
    total_incomes = orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders.aggregate(Sum('paid_value'))['paid_value__sum'] != None else 0
    #get the cost  of destroyed items
    total_destroy_orders = destroy_orders.aggregate(Sum('total_cost'))['total_cost__sum'] if destroy_orders.aggregate(Sum('total_cost'))['total_cost__sum'] != None else 0
    total_returns = return_orders.aggregate(Sum('paid_value'))['paid_value__sum'] if return_orders.aggregate(Sum('paid_value'))['paid_value__sum'] != None else 0
    total_incomes_profit = total_incomes - total_returns
    sum_product_cost = orders.aggregate(Sum('total_cost'))['total_cost__sum'] if orders.aggregate(Sum('total_cost'))['total_cost__sum'] != None else 0
    total_incomes_clear = total_incomes_profit - sum_product_cost
    #gets the total value of the sells
    total_value = orders.aggregate(Sum('value'))['value__sum'] if orders.aggregate(Sum('value'))['value__sum'] != None else 0
    #---------------block center-----------------------------------#
    #gets the income per month etc
    net_income_per_month = []
    product_cost = []
    income_per_month = []
    incomes_per_vendor = []
    net_income_per_vendor = []
    product_cost_per_vendor = []
    incomes_per_category = []
    net_income_per_category = []
    product_cost_per_category = []
    for num in months_list:
        month_count = len(months_list)-num
        month = datetime.datetime.now() - relativedelta(months=month_count)
        sum_month = orders.filter(day_created__month=month.month).aggregate(Sum('paid_value'))['paid_value__sum'] if orders.filter(day_created__month=month.month).aggregate(Sum('paid_value'))['paid_value__sum'] != None else 0
        sum_product = orders.filter(day_created__month=month.month).aggregate(Sum('total_cost'))['total_cost__sum'] if orders.filter(day_created__month=month.month).aggregate(Sum('total_cost'))['total_cost__sum'] != None else 0
        sum_return_paid_value = return_orders.filter(day_created__month=month.month).aggregate(Sum('paid_value'))['paid_value__sum'] if return_orders.filter(day_created__month=month.month).aggregate(Sum('paid_value'))['paid_value__sum'] != None else 0
        sum_return = return_orders.filter(day_created__month=month.month).aggregate(Sum('total_cost'))['total_cost__sum'] if return_orders.filter(day_created__month=month.month).aggregate(Sum('total_cost'))['total_cost__sum'] != None else 0
        sum_month = sum_month - sum_return_paid_value #clean incomes
        income_per_month.append((month.strftime('%B'), sum_month)) # Dictionary paid_value incomes - returns
        net_income_sum = sum_month - sum_product + sum_return
        net_income_per_month.append((month.strftime('%B'), net_income_sum)) #Disctionary incomes - warehouse cost
        product_cost.append((month.strftime('%B'), sum_product))
    for vendor in vendors:
        order_items = RetailOrderItem.objects.filter(title__supplier=vendor, order__in=orders)
        order_return_items = RetailOrderItem.objects.filter(title__supplier=vendor,order__in=return_orders)
        incomes_sum = 0
        product_sum = 0
        return_sum = 0
        for item in order_return_items:
            return_sum += item.price*item.qty
        for item in order_items:
            incomes_sum += item.price * item.qty
            product_sum += item.cost * item.qty
        net_income = incomes_sum - product_sum - return_sum
        incomes_per_vendor.append((vendor.title,incomes_sum))
        product_cost_per_vendor.append((vendor.title,product_sum))
        net_income_per_vendor.append((vendor.title,net_income))
    for category in categories:
        order_items =RetailOrderItem.objects.filter(title__category=category,order__in=orders)
        order_return_items = RetailOrderItem.objects.filter(title__category=category, order__in=return_orders)
        incomes_sum = 0
        product_sum = 0
        return_sum = 0
        for item in order_return_items:
            return_sum += item.price*item.qty
        for item in order_items:
            incomes_sum += item.price * item.qty
            product_sum += item.cost * item.qty
        net_income = incomes_sum - product_sum - return_sum
        incomes_per_category.append((category.title,incomes_sum))
        product_cost_per_category.append((category.title,product_sum))
        net_income_per_category.append((category.title,net_income))
    #-----------------------------------information -paid section-----------------------------------------#
    total_value_orders = []
    total_value_orders_per_vendor = []
    bills_value_orders = []
    bills_value_orders_per_bill = []
    extra_outcomes_value_orders = []
    salary_value_orders =[]
    salary_value_per_occupation =[]
    for num in months_list:
        month  = datetime.datetime.now() - relativedelta(months=num-1)
        total_orders = orders_b.filter(day_created__month=month.month)
        bills_orders = log.filter(date__month=month.month,)
        bills_orders_paid = pay_log.filter(date__month=month.month,)
        total_extra_outcome = pagia_exoda.filter(date__month=month.month)
        total_paid_extra_outcom = total_extra_outcome.filter(active='b')
        salary_total = people_pay.filter(day_expire__month=month.month)
        salary_total_paid  =salary_total.filter(status='b')
        total_value = total_orders.aggregate(Sum('total_price'))['total_price__sum'] if total_orders.aggregate(Sum('total_price'))['total_price__sum'] != None else 0
        total_paid = total_orders.aggregate(Sum('credit_balance'))['credit_balance__sum'] if total_orders.aggregate(Sum('credit_balance'))['credit_balance__sum'] !=None else 0
        total_value_orders.append((month.strftime('%B'), total_value, total_paid))
        bills_value = bills_orders.aggregate(Sum('price'))['price__sum'] if bills_orders.aggregate(Sum('price'))['price__sum'] else 0
        bills_paid = bills_orders_paid.aggregate(Sum('price'))['price__sum'] if bills_orders_paid.aggregate(Sum('price'))['price__sum'] else 0
        bills_value_orders.append((month.strftime('%B'), bills_value, bills_paid))
        extra_outcome_total = total_extra_outcome.aggregate(Sum('price'))['price__sum'] if total_extra_outcome.aggregate(Sum('price'))['price__sum'] else 0
        extra_outcomes_paid = total_paid_extra_outcom.aggregate(Sum('price'))['price__sum'] if total_paid_extra_outcom.aggregate(Sum('price'))['price__sum'] else 0
        extra_outcomes_value_orders.append((month.strftime('%B'), extra_outcome_total, extra_outcomes_paid))
        salary_total = salary_total.aggregate(Sum('value'))['value__sum'] if salary_total.aggregate(Sum('value'))['value__sum'] else 0
        salary_total_paid = salary_total_paid.aggregate(Sum('value'))['value__sum'] if salary_total_paid.aggregate(Sum('value'))['value__sum'] else 0
        salary_value_orders.append((month.strftime('%B'), salary_total, salary_total_paid))
    for vendor in vendors:
        total_vendor_orders = orders_b.filter(vendor=vendor)
        total_value = total_vendor_orders.aggregate(Sum('total_price'))['total_price__sum'] if total_vendor_orders.aggregate(Sum('total_price'))['total_price__sum'] != None else 0
        total_value_paid = total_vendor_orders.aggregate(Sum('credit_balance'))['credit_balance__sum'] if total_vendor_orders.aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
        total_value_orders_per_vendor.append((vendor.title, total_value, total_value_paid))
    for bill in bills:
        bills_orders = log.filter(category=bill)
        bills_orders_paid = log.filter(category=bill, active='b')
        bills_value = bills_orders.aggregate(Sum('price'))['price__sum'] if bills_orders.aggregate(Sum('price'))['price__sum'] else 0
        bills_paid = bills_orders_paid.aggregate(Sum('price'))['price__sum'] if bills_orders_paid.aggregate(Sum('price'))['price__sum'] else 0

        bills_value_orders_per_bill.append((bill.title, bills_value, bills_paid ))
    for occup in occupations:
        salary_total= people_pay.filter(person__occupation =occup)
        salary_total_paid =salary_total.filter(status='b')
        salary_total = salary_total.aggregate(Sum('value'))['value__sum'] if salary_total.aggregate(Sum('value'))['value__sum'] else 0
        salary_total_paid = salary_total_paid.aggregate(Sum('value'))['value__sum'] if  salary_total_paid.aggregate(Sum('value'))['value__sum'] else 0
        salary_value_per_occupation.append((occup.title, salary_total, salary_total_paid))
    # geta the total value of orders per month
    warehouse_orders_per_month = []
    for ele in months_list:
        month  = datetime.datetime.now() - relativedelta(months=ele)
        orders_month = orders.filter(day_created__month=month.month).aggregate(Sum('value'))
        warehouse_orders_per_month.append((month,orders_month['value__sum']))
     #block left side
    total_warehouse_order = orders_b.aggregate(Sum('total_price'))
    total_warehouse_order =total_warehouse_order['total_price__sum']
    if total_warehouse_order == None:
        total_warehouse_order = 0
    #Total outcomes
    pagia_exoda_sum = pagia_exoda.aggregate(Sum('price'))['price__sum']
    log_sum = log.aggregate(Sum('price'))['price__sum']
    people_pay_sum = people_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_sum == None:
        pagia_exoda_sum=0
    if log_sum == None:
        log_sum = 0

    if people_pay_sum == None:
        people_pay_sum = 0
    total_outcomes = pagia_exoda_sum + +log_sum + total_warehouse_order + people_pay_sum
    #Total_paid
    pay_orders_sum = pay_orders.aggregate(Sum('value'))['value__sum']
    if pay_orders_sum == None:
        pay_orders_sum = 0
    pay_log_sum = pay_log.aggregate(Sum('price'))['price__sum']
    if pay_log_sum == None:
        pay_log_sum = 0
    person_pay_sum = person_pay.aggregate(Sum('value'))['value__sum']
    if person_pay_sum == None:
        person_pay_sum = 0
    pagia_exoda_pay_sum = pagia_exoda_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_pay_sum == None:
        pagia_exoda_pay_sum = 0
    total_pays = pay_orders_sum + pay_log_sum + person_pay_sum + pagia_exoda_pay_sum
    context = {
        'currency':CURRENCY,
        'orders':orders,
        #block left side
        'total_warehouse_order':total_warehouse_order,
        'log':log,
        'log_sum':log_sum,
        'pagia_exoda':pagia_exoda,
        'pagia_exoda_sum':pagia_exoda_sum,
        'people':people_pay,
        'people_sum':people_pay_sum,
        'total_outcome':total_outcomes,
        'pay_orders':pay_orders_sum,
        'pay_log':pay_log,
        'pay_log_sum':pay_log_sum,
        'pay_ppl':person_pay,
        'pay_ppl_sum':person_pay_sum,
        'pay_pagia':pagia_exoda_pay,
        'pay_pagia_sum':pagia_exoda_pay_sum,
        'total_pay':total_pays,
        #block right side
        'total_income':total_incomes,
        'total_destroy_orders':total_destroy_orders,
        'total_income_profit':total_incomes_profit,
        'total_income_clear':total_incomes_clear,
        'total_returns':total_returns,
        'total_value':total_value,
        'sum_product':sum_product_cost,
        #block center reports - income section
        'incomes_per_day':income_per_month,
        'net_income_per_month':net_income_per_month,
        'incomes_per_vendor':incomes_per_vendor,
        'net_income_per_vendor':net_income_per_vendor,
        'incomes_per_category':incomes_per_category,
        'net_income_per_category':net_income_per_category,
        #cost section on incomes
        'cost_per_category':product_cost_per_category,
        'cost_per_month':product_cost,
        'cost_per_vendor':product_cost_per_vendor,
        #center block second fragment
        'total_value_orders':total_value_orders,
        'total_value_orders_per_vendor':total_value_orders_per_vendor,
        'bills_value_orders':bills_value_orders,
        'bills_value_orders_per_bill':bills_value_orders_per_bill,
        'extra_outcomes_value_orders':extra_outcomes_value_orders,
        'salary_value_orders':salary_value_orders,
        'salary_value_per_occupation':salary_value_per_occupation,
        'warehouse_orders_per_month':warehouse_orders_per_month,
        'date_pick':date_pick,
    }
    context.update(csrf(request))
    return render(request,'reports/isologismos.html',context)

def balance_sheet_estimate(request):
    #gets the day range you want
    #gets the data from the start of the year
    day_now= datetime.datetime.now()
    start_year = datetime.datetime(datetime.datetime.now().year, 1,1)
    log = Order_Fixed_Cost.objects.all().filter(date__range=[start_year,day_now])
    pagia_exoda =  Pagia_Exoda_Order.objects.all().filter(date__range=[start_year,day_now])
    people_pay = CreatePersonSalaryCost.objects.all().filter(day_expire__range=[start_year,day_now])
    pay_orders = PayOrders.objects.all().filter(date__range=[start_year,day_now])
    pay_log = PayOrderFixedCost.objects.all().filter(date__range=[start_year, day_now])
    person_pay = CreatePersonSalaryCost.objects.all().filter(day_added__range=[start_year, day_now],status ='b')
    pagia_exoda_pay = Pagia_Exoda_Pay_Order.objects.all().filter(day_added__range=[start_year, day_now])
    date_pick = None
    if request.POST:
        date_pick = request.POST.get('date_pick')
        if date_pick:
            if date_pick:
                try:
                    date_range = date_pick.split('-')
                    date_range[0]=date_range[0].replace(' ','')
                    date_range[1]=date_range[1].replace(' ','')
                    start_year =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                    day_now =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
                    orders = RetailOrder.objects.all().filter(day_added__range=[start_year,day_now])
                    log = Order_Fixed_Cost.objects.all().filter(date__range=[start_year,day_now])
                    pagia_exoda =  Pagia_Exoda_Order.objects.all().filter(date__range=[start_year,day_now])
                    people_pay = CreatePersonSalaryCost.objects.all().filter(day_expire__range=[start_year,day_now])
                    pay_orders = PayOrders.objects.all().filter(date__range=[start_year,day_now])
                    pay_log = PayOrderFixedCost.objects.all().filter(date__range=[start_year, day_now])
                    person_pay = CreatePersonSalaryCost.objects.all().filter(day_added__range=[start_year, day_now],status ='b')
                    pagia_exoda_pay = Pagia_Exoda_Pay_Order.objects.all().filter(day_added__range=[start_year, day_now])

                except:
                    date_pick = None
    #incomes
    #gets the actual paid from costumers
    total_incomes = orders.aggregate(Sum('paid_value'))
    total_incomes = total_incomes['paid_value__sum']
    #gets the total value of the sells
    total_value = orders.aggregate(Sum('value'))
    total_value = total_value['value__sum']
    #gets the income per day
    income_per_day = {}
    for num in range((day_now -start_year).days):
        day  = day_now - datetime.timedelta(days=num)
        sum_day = orders.filter(day_added__date = day).aggregate(Sum('paid_value'))
        income_per_day[day.date()] = sum_day['paid_value__sum']
    sorted(income_per_day)
    #geta the total value per day
    value_per_day = {}
    for num in range((day_now -start_year).days):
        day = day_now - datetime.timedelta(days=num)
        sum_day = orders.filter(day_added__date=day).aggregate(Sum('value'))
        value_per_day[day.date()]=sum_day['value__sum']
    sorted(value_per_day)
    #outcomes
    #creates a sorted dictionary by date with the value of total disctionary outcoumes
    sum_per_day = {}
    for num in range((day_now -start_year).days):
        day = day_now - datetime.timedelta(days=num)
        sum_day = orders.filter(day_added__date = day ).aggregate(Sum('total_cost'))
        sum_per_day[day.date()]= sum_day['total_cost__sum']
    sorted(sum_per_day)
    #total orders outcome for the period
    order_lianiki_sum = orders.aggregate(Sum('total_cost'))
    order_lianiki_sum =order_lianiki_sum['total_cost__sum']
    if order_lianiki_sum == None:
        order_lianiki_sum = 0
    # gets the others expenses for the period
    ocuppation = Occupation.objects.all()
    total_sum_by_occup = {}
    for occup in ocuppation:
        title = occup.title
        sum = people_pay.filter(person__occupation__title = title).aggregate(Sum('value'))['value__sum']
        total_sum_by_occup[title]=sum
    sorted(total_sum_by_occup)
    #Total outcomes
    pagia_exoda_sum = pagia_exoda.aggregate(Sum('price'))['price__sum']
    log_sum = log.aggregate(Sum('price'))['price__sum']
    people_pay_sum = people_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_sum == None:
        pagia_exoda_sum=0
    if log_sum == None:
        log_sum = 0
    if order_lianiki_sum == None:
        order_lianiki = 0
    if people_pay_sum == None:
        people_pay_sum = 0
    total_outcomes = pagia_exoda_sum + +log_sum + order_lianiki_sum + people_pay_sum
    #Total_paid
    pay_per_day ={}
    for num in range((day_now -start_year).days):
        day = day_now - datetime.timedelta(days=num)
        pay_day = pay_orders.filter(date = day_now - datetime.timedelta(days=num)).aggregate(Sum('value'))
        pay_per_day[day.date()]= pay_day['value__sum']
    sorted(pay_per_day)
    pay_orders_sum = pay_orders.aggregate(Sum('value'))['value__sum']
    if pay_orders_sum == None:
        pay_orders_sum = 0
    pay_log_sum = pay_log.aggregate(Sum('price'))['price__sum']
    if pay_log_sum == None:
        pay_log_sum = 0
    person_pay_sum = person_pay.aggregate(Sum('value'))['value__sum']
    if person_pay_sum == None:
        person_pay_sum = 0
    total_pay_by_occup = {}
    for occup in ocuppation:
        title = occup.title
        sum = person_pay.filter(person__occupation__title = title).aggregate(Sum('value'))['value__sum']
        total_pay_by_occup[title]=sum
    sorted(total_pay_by_occup)
    pagia_exoda_pay_sum = pagia_exoda_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_pay_sum == None:
        pagia_exoda_pay_sum = 0
    total_pays = order_lianiki_sum + pay_log_sum + person_pay_sum + pagia_exoda_pay_sum
    if total_incomes is not None:
        profit = 100 - ((total_outcomes/total_incomes)*100)
    else:
        profit = 0
    context = {
        'title':'Ισολογισμός',
        'orders':orders,
        'suma':order_lianiki_sum,
        'profit':profit,
        'sum_per_day':sum_per_day,
        'pay_per_day':pay_per_day,
        'log':log,
        'log_sum':log_sum,
        'pagia_exoda':pagia_exoda,
        'pagia_exoda_sum':pagia_exoda_sum,
        'people':people_pay,
        'people_sum':people_pay_sum,
        'total_sum_by_occup':total_sum_by_occup,
        'total_outcome':total_outcomes,
        'pay_orders':pay_orders_sum,
        'pay_log':pay_log,
        'pay_log_sum':pay_log_sum,
        'pay_ppl':person_pay,
        'pay_ppl_sum':person_pay_sum,
        'total_pay_by_occup':total_pay_by_occup,
        'pay_pagia':pagia_exoda_pay,
        'pay_pagia_sum':pagia_exoda_pay_sum,
        'total_pay':total_pays,
        'total_income':total_incomes,
        'total_value':total_value,
        'incomes_per_day':income_per_day,
        'value_per_day':value_per_day,
        'date_pick':date_pick,
    }
    return render(request,'reports/balance_sheet_estimate.html',context)

def balance_sheet_estimate_current_month(request):
    #gets the day range you want
    day_now= datetime.datetime.now()
    orders = RetailOrder.objects.all().filter(day_added__month=day_now.month)
    #incomes
    #gets the actual paid from costumers
    total_incomes = orders.aggregate(Sum('paid_value'))
    total_incomes = total_incomes['paid_value__sum']
    #gets the total value of the sells
    total_value = orders.aggregate(Sum('value'))
    total_value = total_value['value__sum']
    #gets the income per day
    income_per_day = {}
    for num in range(day_now.isoweekday()):
        day  = day_now - datetime.timedelta(days=num)
        sum_day = orders.filter(day_added__date = day).aggregate(Sum('paid_value'))
        income_per_day[day.date()] = sum_day['paid_value__sum']
    sorted(income_per_day)
    #geta the total value per day
    value_per_day = {}
    for num in range(day_now.isoweekday()):
        day = day_now - datetime.timedelta(days=num)
        sum_day = orders.filter(day_added__date=day).aggregate(Sum('value'))
        value_per_day[day.date()]=sum_day['value__sum']
    sorted(value_per_day)
    #outcomes
    #creates a sorted dictionary by date with the value of total disctionary outcoumes
    sum_per_day = {}
    for num in range(day_now.isoweekday()):
        day = day_now - datetime.timedelta(days=num)
        sum_day = orders.filter(day_added__date = day ).aggregate(Sum('total_cost'))
        sum_per_day[day.date()]= sum_day['total_cost__sum']
    sorted(sum_per_day)
    #total orders outcome for the period
    order_lianiki_sum = orders.aggregate(Sum('total_cost'))
    order_lianiki_sum =order_lianiki_sum['total_cost__sum']
    if order_lianiki_sum == None:
        order_lianiki_sum = 0
    # gets the others expenses for the period
    log = Order_Fixed_Cost.objects.all().filter(date__month=day_now.month)
    pagia_exoda =  Pagia_Exoda_Order.objects.all().filter(date__month=day_now.month)
    people_pay = CreatePersonSalaryCost.objects.all().filter(day_expire__month=day_now.month)
    ocuppation = Occupation.objects.all()
    total_sum_by_occup = {}
    for occup in ocuppation:
        title = occup.title
        sum = people_pay.filter(person__occupation__title = title).aggregate(Sum('value'))['value__sum']
        total_sum_by_occup[title]=sum
    sorted(total_sum_by_occup)
    #Total outcomes
    pagia_exoda_sum = pagia_exoda.aggregate(Sum('price'))['price__sum']
    log_sum = log.aggregate(Sum('price'))['price__sum']
    people_pay_sum = people_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_sum == None:
        pagia_exoda_sum=0
    if log_sum == None:
        log_sum = 0
    if order_lianiki_sum == None:
        order_lianiki = 0
    if people_pay_sum == None:
        people_pay_sum = 0
    total_outcomes = pagia_exoda_sum + +log_sum + order_lianiki_sum + people_pay_sum
    #Total_paid
    pay_orders = PayOrders.objects.all().filter(date__month= day_now.month)
    pay_per_day ={}
    for num in range(day_now.isoweekday()):
        day = day_now - datetime.timedelta(days=num)
        pay_day = pay_orders.filter(date = day_now - datetime.timedelta(days=num)).aggregate(Sum('value'))
        pay_per_day[day.date()]= pay_day['value__sum']
    sorted(pay_per_day)
    pay_orders_sum = pay_orders.aggregate(Sum('value'))['value__sum']
    if pay_orders_sum == None:
        pay_orders_sum = 0
    pay_log = PayOrderFixedCost.objects.all().filter(date__month=day_now.month)
    pay_log_sum = pay_log.aggregate(Sum('price'))['price__sum']
    if pay_log_sum == None:
        pay_log_sum = 0
    person_pay = CreatePersonSalaryCost.objects.all().filter(day_added__month=day_now.month,status ='b')
    person_pay_sum = person_pay.aggregate(Sum('value'))['value__sum']
    if person_pay_sum == None:
        person_pay_sum = 0
    total_pay_by_occup = {}
    for occup in ocuppation:
        title = occup.title
        sum = person_pay.filter(person__occupation__title = title).aggregate(Sum('value'))['value__sum']
        total_pay_by_occup[title]=sum
    sorted(total_pay_by_occup)
    pagia_exoda_pay = Pagia_Exoda_Pay_Order.objects.all().filter(day_added__month=day_now.month)
    pagia_exoda_pay_sum = pagia_exoda_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_pay_sum == None:
        pagia_exoda_pay_sum = 0
    total_pays = order_lianiki_sum + pay_log_sum + person_pay_sum + pagia_exoda_pay_sum
    if total_incomes is not None:
        profit = 100 - ((total_outcomes/total_incomes)*100)
    else:
        profit = 0
    context = {
        'orders':orders,
        'suma':order_lianiki_sum,
        'profit':profit,
        'sum_per_day':sum_per_day,
        'pay_per_day':pay_per_day,
        'log':log,
        'log_sum':log_sum,
        'pagia_exoda':pagia_exoda,
        'pagia_exoda_sum':pagia_exoda_sum,
        'people':people_pay,
        'people_sum':people_pay_sum,
        'total_sum_by_occup':total_sum_by_occup,
        'total_outcome':total_outcomes,
        'pay_orders':pay_orders_sum,
        'pay_log':pay_log,
        'pay_log_sum':pay_log_sum,
        'pay_ppl':person_pay,
        'pay_ppl_sum':person_pay_sum,
        'total_pay_by_occup':total_pay_by_occup,
        'pay_pagia':pagia_exoda_pay,
        'pay_pagia_sum':pagia_exoda_pay_sum,
        'total_pay':total_pays,
        'total_income':total_incomes,
        'total_value':total_value,
        'incomes_per_day':income_per_day,
        'value_per_day':value_per_day,
    }
    return render(request,'reports/balance_sheet_estimate.html',context)

def balance_sheet_estimate_current_three_months(request):
    day_now = datetime.datetime.now()
    day_start = day_now  + relativedelta(months=-3)
    #incomes
    orders = RetailOrder.objects.filter(day_added__range =[day_start, day_now])
    total_income = orders.aggregate(Sum('paid_value'))
    total_incomes =total_income['paid_value__sum']
    incomes_per_day = {}
    for num in range((day_now -day_start).days):
        date = day_now - datetime.timedelta(days=num)
        day_sum = orders.filter(day_added__date = date.date()).aggregate(Sum('paid_value'))
        incomes_per_day[date.date()] = day_sum['paid_value__sum']
    sorted(incomes_per_day)
    total_value = orders.aggregate(Sum('value'))
    total_value = total_value['value__sum']
    value_per_day = {}
    for num in range((day_now-day_start).days):
        day = day_now - datetime.timedelta(days=num)
        day_sum = orders.filter(day_added__date = day.date()).aggregate(Sum('value'))
        value_per_day[day.date()]=day_sum['value__sum']
    sorted(value_per_day)
    #outcomes
    #total cost from the orders
    total_cost_orders = orders.aggregate(Sum('total_cost'))
    total_cost_orders = total_cost_orders['total_cost__sum']
    if total_cost_orders == None:
        total_cost_orders = 0
    #total cost from payroll
    person_pay = CreatePersonSalaryCost.objects.all().filter(day_added__range=[day_start,day_now],status ='b')
    person_pay_sum = person_pay.aggregate(Sum('value'))['value__sum']
    if person_pay_sum == None:
        person_pay_sum = 0
    #total_pay per occupation
    ocuppation = Occupation.objects.all()
    total_pay_by_occup = {}
    for occup in ocuppation:
        title = occup.title
        sum = person_pay.filter(person__occupation__title = title).aggregate(Sum('value'))['value__sum']
        total_pay_by_occup[title]=sum
    sorted(total_pay_by_occup)



    #total_cost from fixed assets
    pagia_exoda_pay = Pagia_Exoda_Pay_Order.objects.all().filter(day_added__range=[day_start,day_now])
    pagia_exoda_pay_sum = pagia_exoda_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_pay_sum == None:
        pagia_exoda_pay_sum = 0


    #total bills!!
    pay_log = PayOrderFixedCost.objects.all().filter(date__month=day_now.month)
    pay_log_sum = pay_log.aggregate(Sum('price'))['price__sum']
    if pay_log_sum == None:
        pay_log_sum = 0

    total_pays = total_cost_orders + person_pay_sum +  + pagia_exoda_pay_sum + pay_log_sum

    title = 'Κοστολόγιο Τριμήνου'
    context = {
        'title':title,
        'total_income':total_incomes,
        'total_value':total_value,
        'incomes_per_day':incomes_per_day,
        'value_per_day':value_per_day,

        'total_cost_orders': total_cost_orders,
        'pay_log_sum':pay_log_sum,
        'pay_ppl_sum':person_pay_sum,
        'total_pay_by_occup':total_pay_by_occup,
        'pay_pagia_sum':pagia_exoda_pay_sum,

        'total_pay':total_pays,
    }
    return render(request, 'reports/balance_sheet_estimate.html',context)

def balance_sheet_estimate_six_months(request):
    day_now = datetime.datetime.now()
    day_start = day_now  + relativedelta(months=-6)

    #incomes
    orders = Lianiki_Order.objects.filter(day_added__range =[day_start, day_now])
    total_income = orders.aggregate(Sum('paid_value'))
    total_incomes =total_income['paid_value__sum']


    incomes_per_day = {}
    for num in range((day_now -day_start).days):
        date = day_now - datetime.timedelta(days=num)
        day_sum = orders.filter(day_added__date = date.date()).aggregate(Sum('paid_value'))
        incomes_per_day[date.date()] = day_sum['paid_value__sum']
    sorted(incomes_per_day)

    total_value = orders.aggregate(Sum('value'))
    total_value = total_value['value__sum']

    value_per_day = {}
    for num in range((day_now-day_start).days):
        day = day_now - datetime.timedelta(days=num)
        day_sum = orders.filter(day_added__date = day.date()).aggregate(Sum('value'))
        value_per_day[day.date()]=day_sum['value__sum']
    sorted(value_per_day)



    #outcomes

    #total cost from the orders
    total_cost_orders = orders.aggregate(Sum('total_cost'))
    total_cost_orders = total_cost_orders['total_cost__sum']
    if total_cost_orders == None:
        total_cost_orders = 0

    #total cost from payroll
    person_pay = CreatePersonSalaryCost.objects.all().filter(day_added__range=[day_start,day_now],status ='b')
    person_pay_sum = person_pay.aggregate(Sum('value'))['value__sum']
    if person_pay_sum == None:
        person_pay_sum = 0


    #total_pay per occupation
    ocuppation = Occupation.objects.all()
    total_pay_by_occup = {}
    for occup in ocuppation:
        title = occup.title
        sum = person_pay.filter(person__occupation__title = title).aggregate(Sum('value'))['value__sum']
        total_pay_by_occup[title]=sum
    sorted(total_pay_by_occup)



    #total_cost from fixed assets
    pagia_exoda_pay = Pagia_Exoda_Pay_Order.objects.all().filter(day_added__range=[day_start,day_now])
    pagia_exoda_pay_sum = pagia_exoda_pay.aggregate(Sum('value'))['value__sum']
    if pagia_exoda_pay_sum == None:
        pagia_exoda_pay_sum = 0


    #total bills!!
    pay_log = PayOrderFixedCost.objects.all().filter(date__month=day_now.month)
    pay_log_sum = pay_log.aggregate(Sum('price'))['price__sum']
    if pay_log_sum == None:
        pay_log_sum = 0

    total_pays = total_cost_orders + person_pay_sum +  + pagia_exoda_pay_sum + pay_log_sum

    title = 'Κοστολόγιο Εξαμήνου'
    context = {
        'title':title,
        'total_income':total_incomes,
        'total_value':total_value,
        'incomes_per_day':incomes_per_day,
        'value_per_day':value_per_day,

        'total_cost_orders': total_cost_orders,
        'pay_log_sum':pay_log_sum,
        'pay_ppl_sum':person_pay_sum,
        'total_pay_by_occup':total_pay_by_occup,
        'pay_pagia_sum':pagia_exoda_pay_sum,

        'total_pay':total_pays,
    }
    return render(request, 'reports/balance_sheet_estimate.html',context)

def report_settings(request):
    order_table = ToolsTableOrder.objects.get(title='reports_table_product_order')
    if 'ware_pro' in  request.POST:
        form_pro = ToolsTableOrderForm(request.POST, instance=order_table)
        if form_pro.is_valid():
            form_pro.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form_pro = ToolsTableOrderForm(instance=order_table)
    context = {
        'form_pro':form_pro
    }
    context.update(csrf(request))
    return render(request,'reports/report_settings.html',context)
