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
from .tools import warehouse_filters
import datetime

MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

# Create your views here.


def homepage(request):
    today = datetime.datetime.now()
    start_of_month = '%s-%s-1'%(today.year, today.month)
    incomes = RetailOrder.objects.filter(day_created__range=[start_of_month, today], status_id__in =[6, 7, 8])
    retail_incomes = incomes.filter(order_type='r', status__id=7)
    eshop_incomes = incomes.filter(order_type='e', status__id=7)
    return_items = incomes.filter(order_type='b')
    return_items = RetailOrderItem.objects.filter(order__in=return_items)
    destroy_items = DestroyOrderItem.objects.filter(order__day_added__range=[start_of_month, today])
    total_incomes = incomes.aggregate(Sum('paid_value'))
    total_incomes = total_incomes['paid_value__sum']
    if total_incomes == None:
        total_incomes = 0
    return_incomes = 0
    for item in return_items:
        return_incomes += abs(item.total_price_number())
    if return_incomes == None:
        return_incomes  = 0
    retail_month_incomes = retail_incomes.aggregate(Sum('paid_value'))
    retail_month_incomes = retail_month_incomes['paid_value__sum']
    if retail_month_incomes == None:
        retail_month_incomes = 0
    eshop_month_incomes = eshop_incomes.aggregate(Sum('paid_value'))
    eshop_month_incomes = eshop_month_incomes['paid_value__sum']
    if eshop_month_incomes == None:
        eshop_month_incomes = 0
    destroy_value = 0
    for item in destroy_items:
        destroy_value += item.cost
    #orders warehouse
    orders = Order.objects.filter(day_created__range = [start_of_month, today])
    orders_total_value = orders.aggregate(Sum('total_price'))
    orders_total_value = orders_total_value['total_price__sum']
    if orders_total_value == None:
        orders_total_value = 0
    orders_clear_value  = orders.aggregate(Sum('total_price_after_discount'))
    orders_clear_value = orders_clear_value['total_price_after_discount__sum']
    if orders_clear_value == None:
        orders_clear_value = 0
    orders_taxes_value = orders.aggregate(Sum('total_taxes'))
    orders_taxes_value = orders_taxes_value['total_taxes__sum']
    if orders_taxes_value == None:
        orders_taxes_value = 0
    orders_paid = orders.filter(status__in = ['a', 'd']).aggregate(Sum('total_price'))
    orders_paid = orders_paid['total_price__sum']
    if orders_paid == None:
        orders_paid = 0
    orders_remaining_paid = orders_total_value  - orders_paid
    #bills
    bills = Fixed_Costs_item.objects.filter(category__id = 1 )
    #misthodosia
    payroll =  Occupation.objects.all()
    context= {
        'title':'Αρχική σελίδα Αποθήκης',
        'total_incomes':total_incomes,
        'return_incomes': return_incomes,
        'retail_incomes':retail_month_incomes,
        'eshop_incomes':eshop_month_incomes,
        'destroy_value':destroy_value,
        #orders warehouse
        'orders_total_value': orders_total_value,
        'orders_clear_value': orders_clear_value,
        'orders_taxes_value': orders_taxes_value,
        'orders_total_paid': orders_paid,
        'orders_remaining_paid':orders_remaining_paid,
        'bills': bills,
        'payroll':payroll,
    }
    return render(request,'reports/warehouse.html', context)


def warehouse(request):
    title = "Αποθήκη"
    products = Product.my_query.active_warehouse()
    categories = Category.objects.all()
    vendors = Supply.objects.all()
    orders = Order.objects.all()
    avg_cat = show_avg_per_cat()
    avg_vendor = show_avg_per_vendor()
    avg_order = show_avg_per_order()
    context = {
        'title': title,
        'products': products,
        'categories': categories,
        'vendors': vendors,
        'orders': orders,
        'avg_cat': avg_cat,
        'avg_vendor': avg_vendor,
        'avg_order': avg_order,
    }
    return render(request,'reports/warehouse.html', context)


def ajax_reports_product_info(request):
    if request.POST:
        search_text = request.POST['search_text']
    else:
        search_text = ''
    if len(search_text) <= 2:
        return render_to_response('ajax/ware_product_search.html',{'report_products':None,})
    else:
        products = Product.objects.filter(Q(title__contains=search_text)|
                                          Q(supplier__title__icontains = search_text)|
                                          Q(category__title__icontains = search_text)|
                                          Q(category_site__title__icontains =search_text)).distinct()
        return render_to_response('ajax/ware_product_search.html',{'report_products':products,})


def products(request):
    currency = CURRENCY
    title = "Προιόντα"
    products = Product.my_query.active_warehouse()
    categories = Category.objects.values('title', 'id')
    site_categories = CategorySite.objects.values('title', 'id')
    vendors = Supply.objects.values('title', 'id')
    colors = Color.objects.values('title', 'id')
    sizes = Size.objects.values('title', 'id')
    table_order = ToolsTableOrder.objects.get(title ='reports_table_product_order')
    #use the filters to filter the products without color or size
    products, category_name, vendor_name, color, discount_name, qty_name = warehouse_filters(request, products)
    #create size and color for the products
    products = products.order_by('%s'%(table_order.table_order_by))
    products_info = [0, 0, 0, 0]#total_qty, #total_warehouse_value, #total_sell_value, diffence in %
    products_info[0] = products.aggregate(Sum('qty'))['qty__sum']
    products_info[1] = products.aggregate(total=Sum(F('qty') * F('price_buy')))['total']
    products_info[2] = products.aggregate(total=Sum(F('qty') * F('price')))['total']
    try:
        products_info[3] = ((products_info[2]-products_info[1])/products_info[1])*100
    except:
        products_info[3] = 0
    category_info = {} #total_qty, #total_warehouse_value, #total_sell_value, diffence in %
    for ele_id in category_name:
        get_category = '%s' % Category.objects.get(id=ele_id)
        category_list = [0, 0, 0, 0]#total_qty, #total_warehouse_value, #total_sell_value, diffence in %
        category_list[0] = products.filter(category__id=ele_id).aggregate(Sum('qty'))['qty__sum']
        category_list[1] = products.filter(category__id=ele_id).aggregate(total=Sum(F('qty') * F('price_buy')))['total']
        category_list[2] = products.filter(category__id=ele_id).aggregate(total=Sum(F('qty') * F('price')))['total']
        try:
            category_list[3] = ((category_list[2]-category_list[1])/category_list[1])*100
        except:
            category_list[3] = 0
        category_info[get_category] = category_list
    vendor_info = {}
    for ele_id in vendor_name:
        get_vendor = '%s'%Supply.objects.get(id=ele_id)
        vendor_list = [0,0,0,0]#total_qty, #total_warehouse_value, #total_sell_value, diffence in %
        vendor_list[0] = products.filter(supplier_id=ele_id).aggregate(Sum('qty'))['qty__sum']
        vendor_list[1] = products.filter(supplier_id=ele_id).aggregate(total=Sum(F('qty') * F('price_buy')))['total']
        vendor_list[2] = products.filter(supplier_id=ele_id).aggregate(total=Sum(F('qty') * F('price')))['total']
        try:
            vendor_list[3] = ((vendor_list[2]-vendor_list[1])/vendor_list[1])*100
        except:
            vendor_list[3] = 0
        vendor_info[get_vendor] = vendor_list
    color = []
    size = []
    #if the user have picked color,here we abalyze the qty of the colors picked
    color_analysis=[]
    try:
        for col in color:
            get_color = Color.objects.get(title=col)
            get_product_qty = products.filter(color_a = get_color)
            get_product_qty = get_product_qty.aggregate(Sum('reserve'))
            get_product_qty = get_product_qty['reserve__sum']
            get_product_attr_qty = get_product_attr_qty.aggregate(Sum('qty'))
            get_product_attr_qty =get_product_attr_qty['qty__sum']
            if not get_product_qty:
                get_product_qty = 0
            if not get_product_attr_qty:
                get_product_attr_qty = 0
            color_analysis.append((col,get_product_attr_qty+get_product_qty))
    except:
        pass
    size_analysis = []
    paginator = Paginator(products,table_order.show_number_of_products)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context = locals()
    return render(request, 'reports/products.html', context)


def products_movements(request):
    currency = CURRENCY
    date_start, date_end, date_string = reports_initial_date(request, months=3)
    check_date = date_pick_session(request)
    if check_date:
        date_start, date_end, date_string = check_date
    vendors = Supply.objects.all()
    warehouse_cate = Category.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()
    sellings = RetailOrderItem.my_query.selling_order_items(date_start=date_start, date_end=date_end)
    returns = RetailOrderItem.my_query.return_order_items(date_start=date_start, date_end=date_end)
    buyings = OrderItem.objects.filter(order__day_created__range = [date_start, date_end])
    if request.GET:
        category_name = request.GET.getlist('category')
        vendor_name = request.GET.getlist('vendor')
        color_name = request.GET.getlist('color_name')
        size_name = request.GET.getlist('size_name')
        query = request.GET.get('search_pro')
        date_pick = request.GET.get('date_pick')
        date_pick_form(request, date_pick=date_pick)
        if date_pick:
            date_start, date_end = date_pick_form(request, date_pick=date_pick)
            sellings = RetailOrderItem.objects.filter(order__day_created__range=[date_start, date_end], order__status__id__in=[6,7])
            buyings = OrderItem.objects.filter(order__day_created__range =[date_start, date_end])
            returns = RetailOrderItem.my_query.return_order_items(date_start=date_start, date_end=date_end)
        if query:
            sellings = sellings.filter(
                Q(title__title__contains=query)|
                Q(title__category__title__contains=query) |
                Q(title__supplier__title__contains=query) |
                Q(title__order_code__icontains=query)
            ).distinct()
            buyings = buyings.filter(
                Q(product__title__contains=query)|
                Q(product__category__title__contains=query) |
                Q(product__supplier__title__contains=query) |
                Q(product__order_code__icontains=query)
            ).distinct()
            returns = returns.filter(
                Q(title__title__contains=query)|
                Q(title__category__title__contains=query) |
                Q(title__supplier__title__contains=query) |
                Q(title__order_code__icontains=query)
            ).distinct()
        if category_name:
            buyings = buyings.filter(product__category__id__in=category_name)
            sellings = sellings.filter(title__category__id__in=category_name)
            returns = returns.filter(title__category__id__in=category_name)
        if vendor_name:
            buyings = buyings.filter(product__supplier__id__in=vendor_name)
            sellings = sellings.filter(title__supplier__id__in=vendor_name)
            returns = returns.filter(title__supplier__id__in=vendor_name)
        if color_name:
            sellings = sellings.filter(color__title__in=color_name)
            buyings = buyings.filter(product__color_a__title__in=color_name) + buyings.filter(color__title__in = color_name)
        if size_name:
            get_selling = [ele.title for ele in sellings]
            get_returns = [ele.title for ele in returns]
            size_attr = SizeAttribute.objects.filter(product_related__in=get_selling, title__id__in=size_name)
            products_with_size = [ele.product_related.id for ele in size_attr]

    product_movements = sorted(chain(buyings, sellings, returns),
                             key=attrgetter('day_added'),
                             reverse=True)

    # get the days different and split by 6
    days_modifier = round(((date_end - date_start).days)/6,-1)
    count = 1
    incomes_per_specific_day = []
    returns_per_specific_day = []
    profit_per_specific_day = []
    while count < 7:
        new_day = date_end - relativedelta(days=count*days_modifier)
        incomes_per_specific_day.append(new_day)
        count += 1
    data_per_point = []
    return_per_point = []
    for ele in range(len(incomes_per_specific_day)):
        if ele == 0:
            orders_incomes_ = sellings.filter(order__day_created__range=[incomes_per_specific_day[0], date_end])
            orders_incomes_ = orders_incomes_.aggregate(total=Sum('price', field="price*qty"))['total'] if orders_incomes_.aggregate(total=Sum('price', field="price*qty"))['total'] else 0
            orders_return_ = returns.filter(order__day_created__range=[incomes_per_specific_day[0], date_end]).aggregate(Sum('price'))
            orders_return_ = orders_return_['price__sum']
            if not orders_return_:
                orders_return_ =0
            orders_outcome_ = buyings.filter(order__day_created__range=[incomes_per_specific_day[0], date_end]).aggregate(Sum('price'))
            orders_outcome_ = orders_outcome_['price__sum']
            if not orders_outcome_:
                orders_outcome_ = 0
            data_per_point.append([incomes_per_specific_day[ele], orders_incomes_, orders_outcome_, orders_return_])
        else:
            orders_incomes_ = sellings.filter(order__day_created__range = [incomes_per_specific_day[ele-1], incomes_per_specific_day[ele]])
            orders_incomes_ = orders_incomes_.aggregate(total=Sum('price', field="price*qty"))['total'] if orders_incomes_.aggregate(total=Sum('price', field="price*qty"))['total'] else 0
            #orders_incomes_ = sellings.filter(order__day_created__range=[incomes_per_specific_day[ele-1], incomes_per_specific_day[ele]]).aggregate(Sum('price'))['price__sum'] if sellings.filter(order__day_created__range=[incomes_per_specific_day[ele-1], incomes_per_specific_day[ele]]).aggregate(Sum('price'))['price__sum'] != None else 0
            orders_return_ = returns.filter(order__day_created__range=[incomes_per_specific_day[ele-1], incomes_per_specific_day[ele]]).aggregate(Sum('price'))['price__sum'] if returns.filter(order__day_created__range=[incomes_per_specific_day[ele-1], incomes_per_specific_day[ele]]).aggregate(Sum('price'))['price__sum'] != None else 0
            orders_outcome_ = buyings.filter(order__day_created__range=[incomes_per_specific_day[ele-1], incomes_per_specific_day[ele]]).aggregate(Sum('price'))['price__sum'] if buyings.filter(order__day_created__range=[incomes_per_specific_day[ele-1], incomes_per_specific_day[ele]]).aggregate(Sum('price'))['price__sum'] != None else 0
            data_per_point.append([incomes_per_specific_day[ele], orders_incomes_, orders_outcome_, orders_return_])

    data_per_point = sorted(data_per_point)

    #sellings_per_month = sellings.annotate(month=TruncMonth('day_added')).values('month').annotate(c=Sum('price')).values('month', 'c')
    #buyings_per_months = buyings.annotate(month=TruncMonth('day_added')).values('month').annotate(c=Sum('price')).values('month', 'c')
    products = {} #total_cost_buy ,buy_qty, total_sell, sell_qty
    vendors_stats = {}
    warehouse_cate_stats = {}
    color_stats = {}
    size_stats = {}
    category_site_stats = {}
    product_analysis = {}
    for order_item in buyings:
        if order_item.product not in products.keys():
            products[order_item.product] = [order_item.total_value(),  order_item.qty , 0 ,0]
        else:
            get_data = products[order_item.product]
            get_data[0] += order_item.total_value()
            get_data[1] += order_item.qty
            products[order_item.product] = get_data
        if order_item.product.supplier not in vendors_stats.keys():
            vendors_stats[order_item.product.supplier] = [order_item.total_value(),  order_item.qty , 0 ,0]
        else:
            get_data = vendors_stats[order_item.product.supplier]
            get_data[0] += order_item.total_value()
            get_data[1] += order_item.qty
            vendors_stats[order_item.product.supplier] = get_data
        if order_item.product.category not in warehouse_cate_stats.keys():
            warehouse_cate_stats[order_item.product.category]  = [order_item.total_value(),  order_item.qty , 0 ,0]
        else:
            get_data = warehouse_cate_stats[order_item.product.category]
            get_data[0] += order_item.total_value()
            get_data[1] += order_item.qty
            warehouse_cate_stats[order_item.product.category] = get_data
        if order_item.product.color not in color_stats.keys():
            color_stats[order_item.product.color]  = [order_item.total_value(),  order_item.qty , 0 ,0]
        else:
            get_data = color_stats[order_item.product.color]
            get_data[0] += order_item.total_value()
            get_data[1] += order_item.qty
            color_stats[order_item.product.color] = get_data
        if order_item.size:
            if order_item.size.title not in size_stats.keys():
                size_stats[order_item.size.title] =[order_item.total_value(), order_item.qty, 0, 0]
            else:
                get_data =size_stats[order_item.size.title]
                get_data[0] += order_item.total_value()
                get_data[1] += order_item.qty
                size_stats[order_item.size.title] = get_data
    for order_item in sellings:
        if order_item.title not in products.keys():
            products[order_item.title] = [0, 0, order_item.total_price_number(),  order_item.qty]
        else:
            get_data = products[order_item.title]
            get_data[2] += order_item.total_price_number()
            get_data[3] += order_item.qty
            products[order_item.title] = get_data
        if order_item.title.supplier not in vendors_stats.keys():
            vendors_stats[order_item.title.supplier]  = [0, 0, order_item.total_price_number(),  order_item.qty]
        else:
            get_data = vendors_stats[order_item.title.supplier]
            get_data[2] += order_item.total_price_number()
            get_data[3] += order_item.qty
            vendors_stats[order_item.title.supplier] = get_data
        if order_item.title.category not in warehouse_cate_stats.keys():
            warehouse_cate_stats[order_item.title.category]  = [0, 0, order_item.total_price_number(),  order_item.qty]
        else:
            get_data = warehouse_cate_stats[order_item.title.category]
            get_data[2] +=order_item.total_price_number()
            get_data[3] += order_item.qty
            warehouse_cate_stats[order_item.title.category] = get_data
        if order_item.size:
            if order_item.size.title not in size_stats.keys():
                size_stats[order_item.size.title] = [0, 0, order_item.total_price_number(), order_item.qty]
            else:
                get_data = size_stats[order_item.size.title]
                get_data[2] += order_item.total_price_number()
                get_data[3] += order_item.qty
                size_stats[order_item.size.title] = get_data

    for order_item in returns:
        if order_item.title not in products.keys():
            products[order_item.title] = [0, 0, order_item.total_price_number(),  order_item.qty]
        else:
            get_data = products[order_item.title]
            get_data[2] -= order_item.total_price_number()
            get_data[3] -= order_item.qty
            products[order_item.title] = get_data
        if order_item.title.supplier not in vendors_stats.keys():
            vendors_stats[order_item.title.supplier] = [0, 0, order_item.total_price_number(),  order_item.qty]
        else:
            get_data = vendors_stats[order_item.title.supplier]
            get_data[2] -= order_item.total_price_number()
            get_data[3] -= order_item.qty
            vendors_stats[order_item.title.supplier] = get_data
        if order_item.title.category not in warehouse_cate_stats.keys():
            warehouse_cate_stats[order_item.title.category]  = [0, 0, order_item.total_price_number(),  order_item.qty]
        else:
            get_data = warehouse_cate_stats[order_item.title.category]
            get_data[2] -=order_item.total_price_number()
            get_data[3] -= order_item.qty
            warehouse_cate_stats[order_item.title.category] = get_data
        if order_item.size:
            if order_item.size.title not in size_stats.keys():
                size_stats[order_item.size.title] = [0, 0, order_item.total_price_number(), order_item.qty]
            else:
                get_data = size_stats[order_item.size.title]
                get_data[2] -= order_item.total_price_number()
                get_data[3] -= order_item.qty
                size_stats[order_item.size.title] = get_data
    paginator = Paginator(tuple(products.items()), 50)
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
    return render(request, 'reports/products_flow.html', context)


def products_category(request, dk):
    date_start, date_end, date_string = reports_initial_date(request, months=1)
    check_date = date_pick_session(request)
    if check_date:
        date_start, date_end, date_string = check_date
    #get the products
    category = Category.objects.get(id=dk)
    products = Product.my_query.active_warehouse().filter(category=category)
    buy_order_items = OrderItem.objects.filter(order__day_created__range=[date_start,date_end])
    order_items = RetailOrderItem.objects.filter(order__day_created__range=[date_start, date_end], order__status__id__in = [6,7])
    #fill the filters
    colors = Color.objects.all()
    sizes = Size.objects.all()
    if request.POST:
        get_color = request.POST.getlist('color_name')
        get_size = request.POST.getlist('size_name')
        get_vendor = request.POST.getlist('vendor')
        date_pick = request.POST.get('date_pick')
        date_pick_form(request, date_pick=date_pick)
        if get_vendor:
            products = products.filter(supplier__title__in=get_vendor)
            request.session['vendor_name'] = get_vendor
        if get_size:
            size_attr = SizeAttribute.objects.filter(color__product__category = category, title__in= get_size)
            #color_products = color_products.filter()
    # vendors card
    vendors =[]
    for ele in products:
        if ele.supplier in vendors:
            pass
        else:
            vendors.append(ele.supplier)
    vendors_sum = {}
    for ele in vendors:
        sum = products.filter(supplier=ele).aggregate(Avg('price_buy'))
        sum = sum['price_buy__avg']
        count = products.filter(supplier=ele).aggregate(Sum('qty'))
        count = count['qty__sum']
        total = Decimal(sum)* Decimal(count)
        vendors_sum[ele.title] = (count,total)
    all_vendors = []
    for product in products:
        if product.supplier in all_vendors:
            continue
        else:
            all_vendors.append(product.supplier)
    #analyse the incomes
    product_info=[]
    product_color_analysis =[]
    vendors_info = []
    for product in products:
        items = order_items.filter(title = product)
        count = 0
        total_sells = 0
        total_cost = 0
        clean_incomes = 0
        for item in items:
            if item.title == product:
                total_sells += item.qty*item.price
                count += item.qty
                total_cost += item.qty*item.cost
                clean_incomes += item.qty*item.price - (item.qty*item.cost)- ((item.qty *item.price)*(Decimal(item.order.taxes)/100))
        buy_items= buy_order_items.filter(product=product).aggregate(Sum('qty'))
        buy_items = buy_items['qty__sum']
        product_info.append((product, total_cost, count, total_sells, buy_items or 0, clean_incomes))

    for vendor in all_vendors:
        vendor_buy = buy_order_items.filter(product__supplier=vendor)
        vendor_sells = order_items.filter(title__supplier = vendor)
        products_vendor = products.filter(supplier=vendor)
        cost_remaining_no_taxes = 0
        cost_remaining_with_taxes = 0
        buy_cost = 0
        sells = 0
        sells_without_taxes = 0
        for product in products_vendor:
            cost_remaining_no_taxes += product.qty * Decimal(product.final_price_warehouse())
            cost_remaining_with_taxes += Decimal(product.qty) * Decimal(product.price_with_taxes())
        buy_count = vendor_buy.aggregate(Sum('qty'))
        buy_count = buy_count['qty__sum']
        for item in vendor_buy:
            buy_cost  += item.qty*Decimal(item.price_after_discount())
        sells_count = vendor_sells.aggregate(Sum('qty'))
        sells_count = sells_count['qty__sum']
        if sells_count is None:
            sells_count =0
        for item in vendor_sells:
            sells += item.qty *item.price
            sells_without_taxes += item.qty *item.price -((item.qty *item.price)*(Decimal(item.order.taxes)/100))
        buy_cost_with_taxes = buy_cost*Decimal(1.24)
        vendors_info.append((vendor,(cost_remaining_no_taxes,cost_remaining_with_taxes), buy_count,(buy_cost,buy_cost_with_taxes),sells_count,(sells,sells_without_taxes)))
    product_totals=[0,0,0,0,0]
    for product in product_info:
        # ((product, total_cost, count, total_sells, buy_items, clean_incomes))
        product_totals[0] += product[4]
        product_totals[1] += product[0].qty
        product_totals[2] += product[2]
        product_totals[3] += product[3]
        product_totals[4] += product[5]
    product_analysis_total=[0,0,0,0,0]
    for product in product_color_analysis:
        #color_attr,current_qty,count_buys,count_sells,total_sells,clean_incomes
        product_analysis_total[0] += product[1]
        product_analysis_total[1] += product[2]
        product_analysis_total[2] += product[3]
        product_analysis_total[3] += product[4]
        product_analysis_total[4] += product[5]
    context={
        'colors':colors,
        'sizes':sizes,
        'products_info':product_info,
        'products_total':product_totals,
        'vendor_info':vendors_info,
        'vendors':[vendor[0] for vendor in vendors_info],
        'product_analysis':product_color_analysis,
        'product_analysis_total':product_analysis_total,
        'category_title':category,
        'vendor_sum':vendors_sum,
    }
    return render(request, 'reports/category_product.html', context)


def products_vendors(request, dk):
    title= "Προιόντα"
    products = Product.objects.all().filter(supplier__title = Supply.objects.get(id=dk))
    query =request.GET.get('search_pro')
    if query:
        products=products.filter(
            Q(title__contains=query)|
            Q(category__title__contains=query)|
            Q(supplier__title__contains=query)|
            Q(description__icontains=query)
        ).distinct()

    category = Category.objects.all()
    vendors = Supply.objects.all()
    context ={
        'title':title,
        'products':products,
        'category':category,
        'vendors':vendors,
    }
    return render(request, 'reports/products.html', context)


def product_id(request,dk):
    date_start, date_end, date_string = reports_initial_date(request, months=1)
    check_date = date_pick_session(request)
    if check_date:
        date_start, date_end, date_string = check_date
    if request.POST:
        date_pick = request.POST.get('date_pick')
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            request.session['date_range'] = date_pick
        except:
            pass
    date_end = date_end + relativedelta(days=1)
    product = Product.objects.get(id=dk)
    order_item = OrderItem.objects.filter(product=product, order__day_created__range=[date_start,date_end]) #buys
    retail = RetailOrderItem.objects.filter(title=product, day_added__range=[date_start,date_end]).order_by('-day_added') #sells
    destroy_orders = DestroyOrderItem.objects.filter(title=product, order__day_added__range=[date_start,date_end]).order_by('-day_added')
    change_qty = ChangeQtyOrderItem.objects.filter(title= product)
    #report

    #buys order.  total_cost_from_orders, total_qty, total_cost_with_taxes
    order_item_totals= [0,0,0]#qty, total_value, taxes
    for item in order_item:
        order_item_totals[0] += item.qty
        order_item_totals[1] += item.total_value()
        order_item_totals[2] += item.total_taxes()
    retail_totals =[0,0,0,0,0,0]  #sells_qty, sells_income, sells_fpa, sells_cost, #return_qty, destroy_qty, destroy_cost
    for retail_item in retail:
        if retail_item.order.status.id in [6, 7]:
            retail_totals[0] += retail_item.qty
            retail_totals[1] += retail_item.total_price_number()
            retail_totals[2] += retail_item.total_taxes()
            retail_totals[3] += retail_item.total_cost()
        if retail_item.order.status.id == 8:
            retail_totals[4] += retail_item.qty
            retail_totals[0] += retail_item.qty
            retail_totals[1] += retail_item.total_price_number()
            retail_totals[2] += retail_item.total_taxes()
            retail_totals[3] += retail_item.total_cost()
    return_and_destroy_totals = [0,0,0,]
    for order in destroy_orders:
        return_and_destroy_totals[2] += order.cost*order.qty
    retail_analysis = [0,0,0]
    retail_analysis[0] = retail_totals[1] - retail_totals[2]
    retail_analysis[1] = retail_totals[3]
    retail_analysis[2] = retail_analysis[0] - retail_analysis[1]
    colors_list ={}
    if product.color:
        sizes = SizeAttribute.objects.all().filter(product_related=product)
        for size in sizes:
             try:
                 colors_list[size.product_related.color] += (size.title.title, size.qty)
             except:
                 colors_list[size.product_related.color] = (size.title.title, size.qty)
    context = {
        'currency':CURRENCY,
        'date_range':date_string,
        'product':product,
        'order_item':order_item,
        'order_items_total':order_item_totals,
        'color_list':colors_list,
        'change_qty':change_qty,
        'retail':retail,
        'retail_totals':retail_totals,
        'retail_analysis':retail_analysis,
        'destroy_order_items':destroy_orders,
        'return_and_destroy_totals':return_and_destroy_totals,
    }
    return render(request,'reports/products_id.html', context)


def category_report(request):
    categories = Category.objects.all()
    category_site = CategorySite.objects.all()
    #get initial date from now and three months before.
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')
        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')

    except:
        date_three_months_ago = date_now - relativedelta(months=3)
        date_start = date_three_months_ago
        date_end = date_now
        request.session['date_range'] = None

    date_range = '%s - %s' %(str(date_start).split(' ')[0].replace('-','/'), str(date_end).split(' ')[0].replace('-','/'))
    colors = Color.objects.all()
    size = Size.objects.all()

    initial_order_item_buy = OrderItem.objects.filter(order__day_created__range=[date_start, date_end])
    initial_order_item_sell = RetailOrderItem.objects.filter(order__day_created__range=[date_start, date_end])

    #reports
    category_info = {} #qty, total_cost, qty_sell, sell_incomes, qty_return, qty_destroy, destroy_cost, sell_total_cost
    category_site_info= {} #qty, total_cost, qty_sell, sell_incomes, qty_return, qty_destroy, destroy_cost, sell_total_cost

    for item in initial_order_item_buy:
        if item.product.category not in category_info.keys():
            category_info[item.product.category] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
        else:
            get_data = category_info[item.product.category]
            get_data[0] += item.qty
            get_data[1] += item.total_value()
            category_info[item.product.category] = get_data

        if item.product.category_site not in category_site_info.keys() and item.product.category_site:
            if item.product.category_site.is_parent:
                category_site_info[item.product.category_site] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
            elif item.product.category_site.is_first_born:
                first_born = item.product.category_site.category
                category_site_info[item.product.category_site] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                if first_born not in category_site_info.keys():
                     category_site_info[first_born] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                else:
                    get_data = category_site_info[first_born]
                    get_data[0] += item.qty
                    get_data[1] += item.total_value()
                    category_site_info[first_born] = get_data

            elif item.product.category_site.is_second_son:
                first_born = item.product.category_site.category
                second_son = item.product.category_site.category.category
                if first_born not in category_site_info.keys():
                     category_site_info[first_born] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                else:
                    get_data = category_site_info[first_born]
                    get_data[0] += item.qty
                    get_data[1] += item.total_value()
                    category_site_info[first_born] = get_data

                if second_son not in category_site_info.keys():
                     category_site_info[second_son] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                else:
                    get_data = category_site_info[second_son]
                    get_data[0] += item.qty
                    get_data[1] += item.total_value()
                    category_site_info[second_son] = get_data
        elif item.product.category_site:
            if item.product.category_site.is_parent:
                get_data = category_site_info[item.product.category_site]
                get_data[0] += item.qty
                get_data[1] += item.total_value()
                category_site_info[item.product.category_site] = get_data
            elif item.product.category_site.is_first_born:
                parent = item.product.category_site.category
                get_data_parent = category_site_info[parent]
                get_data_parent[0] += item.qty
                get_data_parent[1] += item.total_value()
                category_site_info[parent] = get_data_parent
                get_data = category_site_info[item.product.category_site]
                get_data[0] += item.qty
                get_data[1] += item.total_value()
                category_site_info[item.product.category_site] = get_data
            elif item.product.category_site.is_second_son:
                grand_father = item.product.category_site.category.category
                get_data_grand = category_site_info[grand_father]
                get_data_grand[0] += item.qty
                get_data_grand[1] += item.total_value()
                category_site_info[grand_father] = get_data_grand
                parent = item.product.category_site.category
                get_data_parent = category_site_info[parent]
                get_data_parent[0] += item.qty
                get_data_parent[1] += item.total_value()
                category_site_info[parent] = get_data_parent
                get_data = category_site_info[item.product.category_site]
                get_data[0] += item.qty
                get_data[1] += item.total_value()
                category_site_info[item.product.category_site] = get_data
    for sell in initial_order_item_sell:
        if sell.title.category not in category_info.keys():
            if sell.order.status.id == 7:
                category_info[sell.title.category] = [0,0,sell.qty, sell.total_price_number(), 0, 0, 0,  sell.total_cost()]
            if sell.order.status.id == 8:
                category_info[sell.title.category] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
        else:
            if sell.order.status.id == 7:
                get_data = category_info[sell.title.category]
                get_data[2] += sell.qty
                get_data[3] += sell.total_price_number()
                get_data[7] += sell.total_cost()
                category_site_info[sell.title.category] = get_data
            if sell.order.status.id == 8:
                get_data = category_info[sell.title.category]
                get_data[4] += abs(sell.qty)
                get_data[5] += abs(sell.total_price_number())
                category_site_info[sell.title.category] = get_data
        if sell.order.status.id == 7:
            if sell.title.category_site not in category_site_info.keys() and sell.title.category_site:
                if sell.title.category_site.is_parent:
                    category_site_info[sell.title.category_site] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0, sell.total_cost()]
                if sell.title.category_site.is_first_born:
                    parent = sell.title.category_site.category
                    category_site_info[sell.title.category_site] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0, sell.total_cost()]
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0, sell.total_cost()]
                    else:
                        get_data = category_site_info[parent]
                        get_data[2] += sell.qty
                        get_data[3] += sell.total_price_number()
                        category_site_info[parent] = get_data
                if sell.title.category_site.is_second_child:
                    grand_father = sell.title.category_site.category.category
                    parent = sell.title.category_site.category
                    category_site_info[sell.title.category_site] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0, sell.total_cost()]
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0, sell.total_cost()]
                    else:
                        get_data = category_site_info[parent]
                        get_data[2] += sell.qty
                        get_data[3] += sell.total_price_number()
                        category_site_info[parent] = get_data
                    if grand_father not in category_site_info.keys():
                        category_site_info[grand_father] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0, sell.total_cost()]
                    else:
                        get_data = category_site_info[grand_father]
                        get_data[2] += sell.qty
                        get_data[3] += sell.total_price_number()
                        category_site_info[grand_father] = get_data
        if sell.order.status.id == 8:
            if sell.title.category_site not in category_site_info.keys():
                if sell.title.category_site.is_parent:
                    category_site_info[sell.title.category_site] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                if sell.title.category_site.is_first_born:
                    category_site_info[sell.title.category_site] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                    parent = sell.title.category_site.category
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                    else:
                        get_data = category_site_info[parent]
                        get_data[4] += abs(sell.qty)
                        get_data[5] += abs(sell.total_price_number())
                        category_site_info[parent] = get_data
                if sell.title.category_site.is_second_child:
                    category_site_info[sell.title.category_site] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                    grand_father = sell.title.category_site.category.category
                    if grand_father not in category_site_info.keys():
                        category_site_info[grand_father] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                    else:
                        get_data = category_site_info[grand_father]
                        get_data[4] += abs(sell.qty)
                        get_data[5] += abs(sell.total_price_number())
                        category_site_info[grand_father] = get_data
                    parent = sell.title.category_site.category
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                    else:
                        get_data = category_site_info[parent]
                        get_data[4] += abs(sell.qty)
                        get_data[5] += abs(sell.total_price_number())
                        category_site_info[parent] = get_data
    context ={
        'date_range':date_range,
        'currency':CURRENCY,
        'categories':categories,
        'category_site':category_site,
        'category_info':category_info,
        'category_site_info':category_site_info,
        'title':'Κατηγορίες',
        'colors':colors,
        'size':size,
    }
    return render(request, 'reports/category_report.html', context)


def vendors(request):
    day_start, day_end, date_string = reports_initial_date(request, months=1)
    check_date = date_pick_session(request)
    if check_date:
        day_start, day_end, date_string = check_date
    initial_buys = Order.objects.filter(day_created__range=[day_start, day_end])
    initial_sells = RetailOrderItem.objects.filter(order__day_created__range=[day_start, day_end], order__status__id__in=[6,7])
    vendors = Supply.objects.all()
    vendors_info = {} #order_qty, order_total_cost, order_pay, qty_sells, total_sells, returns, destroy
    for buy in initial_buys:
        if buy.vendor not in vendors_info.keys():
            vendors_info[buy.vendor] = [buy.items_count(),buy.total_price, buy.credit_balance, 0, 0, 0, 0, 0]
        else:
            get_data = vendors_info[buy.vendor]
            get_data[0] += buy.items_count()
            get_data[1] += buy.total_price
            get_data[2] += buy.credit_balance
            vendors_info[buy.vendor] = get_data
    for sell in initial_sells:
        if sell.order.status.id == 7:
            if sell.title.supplier not in vendors_info.keys():
                vendors_info[sell.title.supplier] = [0, 0, 0, sell.qty, sell.total_price_number(),0, 0, sell.total_cost()]
            else:
                get_data = vendors_info[sell.title.supplier]
                get_data[3] += sell.qty
                get_data[4] += sell.total_price_number()
                get_data[7] += sell.total_cost()
                vendors_info[sell.title.supplier] = get_data
        if sell.order.status.id == 8:
            if sell.title.supplier not in vendors_info.keys():
                vendors_info[sell.title.supplier] = [0, 0, 0, 0, 0, sell.qty, 0, 0]
            else:
                get_data = vendors_info[sell.title.supplier]
                get_data[5] += abs(sell.qty)
                vendors_info[sell.title.supplier] = get_data
    taxes_city = TaxesCity.objects.all()
    title= "ΠρομηΘευτές"
    query =request.GET.get('search_pro')
    if query:
        vendors=vendors.filter(
            Q(title__icontains=query)|
            Q(afm__icontains=query)|
            Q(phone__icontains=query)|
            Q(fax__icontains=query)|
            Q(email__icontains=query)|
            Q(phone1__icontains=query)
        ).distinct()
    print(vendors, vendors_info)
    context = {
        'title':title,
        'currency':CURRENCY,
        'vendors':vendors,
        'taxes_city':taxes_city,
        'vendors_info':vendors_info,
        'date_range':date_string,
    }
    return render(request, 'reports/vendors.html', context)


def vendors_per_doy(request, dk):
    doy = TaxesCity.objects.get(id=dk)
    taxes_city = TaxesCity.objects.all()
    vendors =Supply.objects.all().filter(doy=doy)
    title = doy.title
    query =request.GET.get('search_pro')
    if query:
        vendors=vendors.filter(
            Q(title__icontains=query)|
            Q(afm__icontains=query)|
            Q(phone__icontains=query)|
            Q(fax__icontains=query)|
            Q(email__icontains=query)|
            Q(phone1__icontains=query)
        ).distinct()
    context ={
        'title':title,
        'vendors':vendors,
        'taxes_city':taxes_city,

    }
    return render(request, 'reports/vendors.html', context)


def date_initial_range(request, month=3):
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')
        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
    except:
        date_three_months_ago = date_now - relativedelta(months=month)
        date_range =[date_three_months_ago,date_now]
        date_start = date_three_months_ago
        date_end = date_now
        request.session['date_range'] = None
    return [date_start, date_end]


def vendors_id(request,dk):
    #on initial start of the page gives all the moves of the last 3 months
    currency = CURRENCY
    date_start, date_end = date_initial_range(request)
    vendor = Supply.objects.get(id=dk)
    #product section
    products = vendor.product_set.all()
    total_remaining_cost = products.aggregate(total=Sum(F('price_buy')*F('qty')))['total']
    total_remaining_markup = products.aggregate(total=Sum(F('price')*F('qty')))['total']
    if request.POST:
        date_pick = request.POST.get('date_pick')
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            request.session['date_range'] = '%s --- %s' %(date_start.date(),date_end.date())
        except:
            date_pick = None
    #product_movements
    incomes_info = [0,0,0,0]
    products_analysis = []
    total_days = str(date_end - date_start)
    total_days = total_days.split(' ')[0]
    for product in products:
        product_qty = 0
        product_return = 0
        product_destroy = 0
        product_cost = 0
        product_value = 0

        retail_item = RetailOrderItem.objects.filter(title=product, day_added__range=[date_start, date_end], order__order_type__in=['e', 'r'])
        return_item = RetailOrderItem.objects.filter(title=product, day_added__range=[date_start, date_end], order__order_type='b')
        for item in return_item:
            product_return +=  item.qty
        destroy_item = DestroyOrderItem.objects.filter(title=product,day_added__range=[date_start,date_end])
        for item in destroy_item:
            product_destroy += item.qty
        for retail in retail_item:
            product_qty += retail.qty
            product_cost += retail.qty*retail.cost
            product_value +=retail.qty*retail.price
        try:
            product_sales_per_day = product_qty/int(total_days)
        except:
            product_sales_per_day=0
        try:
            product_available = (product.qty)/(product_sales_per_day)
        except:
            product_available = None
        try:
            product_return_pc = (product_return/product_qty)*100
            product_destroy_pc = (product_destroy/product_qty)*100
        except:
            product_return_pc = 0
            product_destroy_pc = 0
        products_analysis.append((product,
                                  product_sales_per_day,
                                  product_available,
                                  product_cost,
                                  product_value,
                                  product_return,
                                  product_destroy,
                                  product_return_pc,
                                  product_destroy_pc,
                                  product_qty
                                    ))
    order = vendor.order_set.all().filter(day_created__range=[date_start,date_end]).order_by('-day_created')
    #gets all the payments for the current year!
    payments = PayOrders.objects.filter(title__vendor=vendor)
    deposits = VendorDepositOrder.objects.filter(vendor=vendor)
    check_orders = CheckOrder.objects.all().filter(debtor=vendor)
    payment_list = sorted(chain(payments,deposits,check_orders),
                           key=attrgetter('day_added'),
                           reverse=True)
    #incomes
    retail_orders = RetailOrderItem.objects.filter(title__in=products, order__order_type__in=['e', 'r'])
    return_orders= RetailOrderItem.objects.filter(title__in=products, order__order_type='b')
    destroy_orders = DestroyOrderItem.objects.filter(title__in=products)
    pos_order_list = sorted(chain(retail_orders, return_orders, destroy_orders),
                            key=attrgetter('day_added'),
                            reverse=True)
    products_pre_order =[]
    if 'pre_order_estimate' in request.POST:
        days_before = request.POST.get('days_before')
        days_after = request.POST.get('days_after')
        date_before = date_start - relativedelta(days=int(days_before))
        date_after = date_start + relativedelta(days=int(days_after))
        for product in products:
            product_qty = 0
            retail_item = RetailOrderItem.objects.filter(title=product, day_added__in=[date_before,date_start])
            for retail in retail_item:
                product_qty += retail.qty
            product_sales_per_day = product_qty/int(days_before)
            try:
                product_available = (product.reserve)/(product_sales_per_day)
            except:
                product_available = None
            product_demand = Decimal(days_after)* Decimal((product_sales_per_day))
            try:
                product_forecast = product_demand
                product_offer = round(product_forecast)
            except:
                product_forecast = 'Δεν έχουν γίνει πωλήσεις σε αυτό το διάστημα'
                product_offer = 0
            products_pre_order.append((product,
                                       product_sales_per_day,
                                       product_available,
                                       product_forecast,
                                       product_offer))
    if 'add_to_pre_order' in request.POST:
        products_choosed = request.POST.getlist('pro_cho')
    context = locals()
    context.update(csrf(request))
    return render(request, 'reports/vendors_id.html',context)


def add_to_pre_order(request,dk,pk):
    product = Product.objects.get(id=dk)
    try:
        order = PreOrder.objects.filter(status='a').last()
        if request.POST:
            form = PreOrderItemForm(request.POST,initial={'title':product,
                                                          'order':order,})
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/reports/vendors/%s'%(pk))
        else:
            form =PreOrderItemForm(initial={'title':product,
                                            'order':order,})
        context={
            'form':form,
            'title':'Προσθήκη στην Προπαραγγελία.',
            'return_page':'/reports/vendors/%s'%(pk),
        }
        context.update(csrf(request))
        return render(request, 'inventory/create_costumer_form.html', context)
    except:
        messages.warning(request,'Δημιουργήστε Προπαραγγελία πρώτα.')
        return HttpResponseRedirect('/reports/vendors/%s'%(pk))


def orders(request):
    orders_i = Order.objects.all().order_by('-day_created')
    vendors = Supply.objects.all()
    payment_method = PaymentMethod.objects.all()
    choices = Order.CHOICES

    title= 'Τιμολόγια'
    query =request.GET.get('search_pro')
    if query:
        orders_i = orders_i.filter(
            Q(code__icontains = query)|
            Q(vendor__title__icontains =query)
        ).distinct()

    #filters
    vendor_name = request.POST.getlist('vendor_name')
    if vendor_name:
        orders_i = orders_i.filter(vendor__title__in=vendor_name)
    payment_name = request.POST.getlist('payment_name')
    if payment_name:
        orders_i = orders_i.filter(payment_method__title__in = payment_name)

    status_name = request.POST.getlist('status_name')
    if status_name:
        orders_i =orders_i.filter(status__in=status_name)
    date_pick = request.POST.get('date_pick')
    try:
        date_range = date_pick.split('-')
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')
        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
        orders_i = orders_i.filter(date__range=[date_start,date_end])
    except:
        pass

    total_orders = orders_i.count()
    sum_orders = orders_i.aggregate(Sum('total_price'))
    sum_orders =sum_orders['total_price__sum']
    average_orders = orders_i.aggregate((Avg('total_price')))
    average_orders =average_orders['total_price__avg']
    taxes = orders_i.aggregate(Sum('total_taxes'))
    taxes = taxes['total_taxes__sum']

    if 'd' in status_name:
        remaining = orders_i.aggregate(Sum('credit_balance'))
        remaining=remaining['credit_balance__sum']
        remaining =sum_orders - remaining
    else:
        remaining =None
    print(status_name)
    context={
        'choices':choices,
        'choice_name':status_name,
        'remaining':remaining,
        'orders':orders_i,
        'title':title,
        'vendors':vendors,
        'payment_method':payment_method,
        'total_orders':total_orders,
        'sum_orders':sum_orders,
        'avg_orders':average_orders,
        'taxes':taxes,
    }
    return render(request, 'reports/orders.html', context)

#needs to deleted check the urls for total  annihilation
def orders_per_category(request, dk):
    vendor = Supply.objects.get(id=dk)
    orders_i = Order.objects.all().filter(vendor=vendor).order_by('-date')
    vendors = Supply.objects.all()
    title= 'Τιμολόγια'
    query =request.GET.get('search_pro')
    if query:
        orders_i = orders_i.filter(
            Q(code__icontains = query)|
            Q(vendor__title__icontains =query)
        ).distinct()

    context={
        'orders':orders_i,
        'title':title,
        'vendors':vendors,
    }
    return render(request, 'reports/orders.html', context)


def order_id(request,dk):
    order = Order.objects.get(id=dk)
    title = order.code
    products = order.orderitem_set.all()
    pay_info = order.payorders_set.all()
    pay_deposit = order.vendordepositorderpay_set.all()
    context={
        'title': title,
        'products': products,
        'pay_info': pay_info,
        'order': order,
        'deposit': pay_deposit,
    }
    return render(request, 'reports/orders_id.html', context)


def reports_order_reset_payments(request, dk):
    order = Order.objects.get(id=dk)
    pay_orders = order.payorders_set.all()
    for pay_order in pay_orders:
        pay_order.delete_pay()
        pay_order.delete()
    pay_orders_deposit = order.vendordepositorderpay_set.all()
    for pay_order in pay_orders_deposit:
        pay_order.delete_deposit()
        pay_order.delete()
    order.credit_balance = 0
    order.status = 'p'
    order.save()
    return redirect('order_edit_main', dk=dk)
