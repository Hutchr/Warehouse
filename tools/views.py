from django.shortcuts import render, HttpResponseRedirect

# Create your views here.

from transcations.models import *
from inventory_manager.models import *
from tools.models import ToolsTableOrder
from PoS.models import Order_status
from cart.models import CartRules
from account.models import CostumerAccount
from comment.models import CommentType
from dateutil.relativedelta import relativedelta
import datetime



#returns a list with 3 items, first two used for the querys and the third is a string represent
def reports_initial_date(request, months):
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')
        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')

    except:
        date_three_months_ago = date_now - relativedelta(months=months)
        date_start = date_three_months_ago
        date_end = date_now
        request.session['date_range'] = None

    date_range = '%s - %s' %(str(date_start).split(' ')[0].replace('-','/'), str(date_end).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]

def date_pick_session(request):
    date_pick = request.POST.get('date_pick')
    try:
        date_range = date_pick.split('-')
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')

        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
        request.session['date_range'] = '%s --- %s' %(date_start.date(),date_end.date())
        date_range = '%s - %s' %(str(date_start).split(' ')[0].replace('-','/'), str(date_end).split(' ')[0].replace('-','/'))
        return [date_start, date_end, date_range]
    except:
        return None

def date_pick_form(request, date_pick): # gets the day form date_pick input and convert it to string its
    if date_pick:
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            request.session['date_range'] = date_pick
            date_end = date_end + relativedelta(days=1)
            return [date_start, date_end]
        except:
            date_pick = None


def set_up_database(request):
    #creates the models that the database need to start_working
    #disable that url after the use for no duplicate models.

    new_costumer = CostumerAccount.objects.create(first_name='Πελάτες', last_name= 'Λιανικής',is_retail=True, is_eshop=False )
    new_costumer.save()
    new_costumer = CostumerAccount.objects.create(first_name='Πελάτες', last_name= 'Χονδρικής',is_retail=False, is_eshop=False )
    new_costumer.save()

    table_order = ToolsTableOrder.objects.create(title='warehouse_table_product_order', table_order_by='id')
    table_order.save()
    table_order = ToolsTableOrder.objects.create(title='warehouse_table_vendor_order',table_order_by='id')
    table_order.save()
    table_order = ToolsTableOrder.objects.create(title='warehouse_table_order_order', table_order_by='id')
    table_order.save()
    table_order = ToolsTableOrder.objects.create(title='reports_table_product_order', table_order_by='id')
    table_order.save()

    payment_method = PaymentMethodGroup.objects.create(title='Bank')
    payment_method.save()

    # Τεμάχ,Κιλά, Κιβώτ
    unit_a = Unit.objects.create(name= 'Τεμάχ')
    unit_a.save()
    unit_b = Unit.objects.create(name ='Κιλά')
    unit_b.save()
    unit_c = Unit.objects.create(name= 'Κιβώτ')
    unit_c.save()

    #Λογαριασμοί, Προσωπικό, Αγορές
    fixed_cost = Fixed_costs.objects.create(title= 'Λογαριασμοί')
    fixed_cost.save()
    fixed_cost = Fixed_costs.objects.create(title= 'Προσωπικό')
    fixed_cost.save()
    fixed_cost = Fixed_costs.objects.create(title= 'Αγορές')
    fixed_cost.save()

    # Μισθός, IKA/TEBE, Extra,
    cate = CategoryPersonPay.objects.create(title ='Μισθός',  )
    cate.save()
    cate = CategoryPersonPay.objects.create(title ='IKA/TEBE')
    cate.save()
    cate = CategoryPersonPay.objects.create(title ='Extra')
    cate.save()

    #Αγορές, Επισκευές, Διάφορα Έξοδα

    fixed_assets = Pagia_Exoda.objects.create(title = 'Αγορές', category = Fixed_costs.objects.get(id=3))
    fixed_assets.save()
    fixed_assets = Pagia_Exoda.objects.create(title = 'Επισκευές',category = Fixed_costs.objects.get(id=3))
    fixed_assets.save()
    fixed_assets = Pagia_Exoda.objects.create(title = 'Διάφορα Έξοδα',category = Fixed_costs.objects.get(id=3))
    fixed_assets.save()
    cash = PaymentMethod.objects.create(title='Μετρητά')
    cash.save()

    new_order_status = Order_status.objects.create(title='Νέα Παραγγελία',id='1')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Σε επεξεργασία',id='2')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Αναμονή',id='3')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Αλλαγή',id='4')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Έτοιμο προς Αποστολή',id='5')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Απεστάλη',id='6')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Εισπράκτηκε.',id='7')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Επιστράφηκε.',id='8')
    new_order_status.save()
    new_order_status = Order_status.objects.create(title='Ακυρώθηκε.',id='9')
    new_order_status.save()
    new_comment_type = CommentType.objects.create(title='Πελάτης')
    new_comment_type.save()
    new_comment_type = CommentType.objects.create(title='Stuff')
    new_comment_type.save()
    new_comment_type = CommentType.objects.create(title='Επισκεύτης')
    new_comment_type.save()

    new_cart_rule = CartRules.objects.create(title='Ελλάδα')
    new_cart_rule.save()


    return HttpResponseRedirect('/')

def diff_month(date_start, date_end):
    return (date_end.year - date_start.year)*12 + (date_end.month - date_start.month)

def decimal_or_zero(string_number):
    try:
        number = Decimal(string_number)
    except:
        number = 0
    return number

def clear_sessions(request):
    request.session['pro_cat_fi'] = None
    request.session['pro_ven_fi'] = None
    request.session['pro_site_fi'] = None
    request.session['pro_ware_fi'] = None
    request.session['pro_btw_fi'] = None
    request.session['check_ven_fi'] = None
    request.session['ware_order_ven']=None
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def warehouse_product_table_order(request,text):

    table_order_by = ToolsTableOrder.objects.get(title='warehouse_table_product_order')
    if text == 'edit':
        table_order_by.table_order_by ='id'
        table_order_by.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if text == table_order_by.table_order_by:
        text='-'+str(text)
    table_order_by.table_order_by = text
    table_order_by.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def warehouse_vendor_table_order(request,text):
    table_order_by = ToolsTableOrder.objects.get(title='warehouse_table_vendor_order')
    if text == 'edit':
        table_order_by.table_order_by ='id'
        table_order_by.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if text == table_order_by.table_order_by:
        text='-'+str(text)
    table_order_by.table_order_by = text
    table_order_by.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def warehouse_table_order(request,text,dk):
    table_order_by = ToolsTableOrder.objects.get(id=dk)
    if text == 'edit':
        table_order_by.table_order_by ='id'
        table_order_by.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if text == table_order_by.table_order_by:
        text='-'+str(text)
    table_order_by.table_order_by = text
    table_order_by.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def clear_session_create_pro(request):
    request.session['create_pro_title'] = None
    request.session['create_pro_cate'] = None
    request.session['create_pro_ven']= None
    request.session['create_pro_size']= None
    request.session['create_pro_color'] = None
    request.session['create_pro_notes'] =None
    #request.session['create_pro_price_buy'] = product.price_buy
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def clear_session_reports_pro(request):
    request.session['report_pro_cat']= None
    request.session['report_pro_ven']= None
    request.session['report_pro_ware'] = None
    request.session['report_pro_color']=None
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def clear_sessions_reports_income(request):
    request.session['report_income_costu'] = None
    request.session['report_income_type'] = None
    request.session['report_income_ship'] = None
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def clear_sessions_reports_products(request):
    request.session['report_pro_cat'] = None
    request.session['report_pro_ven'] = None
    request.session['report_pro_color'] = None
    request.session['report_pro_size'] = None
    request.session['report_pro_ware'] = None

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def clear_sessions_site_admin_orders(request):
    request.session['shipping_order_admin'] = None
    request.session['payment_order_admin'] = None
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))