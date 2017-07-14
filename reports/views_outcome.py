from django.shortcuts import render
from django.db.models import Q, F
from transcations.models import *
from django.db.models import  Sum
from django.template.context_processors import csrf
from PoS.models import *
from dateutil.relativedelta import relativedelta
import datetime
MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']


#---------------------------------Outcomes section--------------------------------------------

def outcome(request):
    day_now = datetime.datetime.now()
    year_start = datetime.datetime(datetime.datetime.now().year, 1, 1)
    title ="Συνολική Εικόνα Επιχείρησης"
    #overall data for bills
    bills_all = Order_Fixed_Cost.objects.all().filter(date__range=[year_start,day_now]).aggregate(Sum('price'))['price__sum'] if Order_Fixed_Cost.objects.all().filter(date__range=[year_start,day_now]).aggregate(Sum('price'))['price__sum'] else 0
    bills_paid = Order_Fixed_Cost.objects.all().filter(date__range=[year_start,day_now],active='b' ).aggregate(Sum('price'))['price__sum'] if Order_Fixed_Cost.objects.all().filter(date__range=[year_start,day_now],active='b' ).aggregate(Sum('price'))['price__sum'] else 0
    bills_pending = Order_Fixed_Cost.objects.all().filter(date__range=[year_start, day_now], active='a').aggregate(Sum('price'))['price__sum'] if Order_Fixed_Cost.objects.all().filter(date__range=[year_start, day_now], active='a').aggregate(Sum('price'))['price__sum'] else 0
    #overall data for expenses
    expenses_all = Pagia_Exoda_Order.objects.all().filter(date__range=[year_start,day_now]).aggregate(Sum('price'))['price__sum'] if Pagia_Exoda_Order.objects.all().filter(date__range=[year_start,day_now]).aggregate(Sum('price'))['price__sum'] else 0
    expenses_paid = Pagia_Exoda_Order.objects.all().filter(date__range=[year_start,day_now],active='b' ).aggregate(Sum('price'))['price__sum'] if Pagia_Exoda_Order.objects.all().filter(date__range=[year_start,day_now],active='b' ).aggregate(Sum('price'))['price__sum'] else 0
    expenses_pending = Pagia_Exoda_Order.objects.all().filter(date__range=[year_start, day_now], active='a').aggregate(Sum('price'))['price__sum'] if Pagia_Exoda_Order.objects.all().filter(date__range=[year_start, day_now], active='a').aggregate(Sum('price'))['price__sum'] else 0
    #overall data for people
    person_all = CreatePersonSalaryCost.objects.all().filter(day_added__range=[year_start,day_now]).aggregate(Sum('value'))
    person_all = person_all['value__sum']
    person_paid = CreatePersonSalaryCost.objects.all().filter(day_added__range=[year_start,day_now], status='b').aggregate(Sum('value'))
    person_paid = person_paid['value__sum']
    person_pending = CreatePersonSalaryCost.objects.all().filter(day_added__range=[year_start,day_now], status='a').aggregate(Sum('value'))['value__sum'] if CreatePersonSalaryCost.objects.all().filter(day_added__range=[year_start,day_now], status='a').aggregate(Sum('value'))['value__sum'] else 0

    #blls analytic
    fixed_costs = Fixed_Costs_item.objects.all()
    orders_data = Order_Fixed_Cost.objects.all().filter(date__range=[year_start,day_now])
    bills_analytics = {}
    for bill in fixed_costs:
        bill_sum = orders_data.filter(category=bill, active='a').aggregate(Sum('price'))
        bill_sum = bill_sum['price__sum']
        bills_analytics[bill.title]=bill_sum
    #expenses analytic
    expenses_data = Pagia_Exoda_Order.objects.all().filter(date__range=[year_start,day_now])
    pagia_exoda = Pagia_Exoda.objects.all()
    expense_analytics ={}
    for expense in pagia_exoda:
        expenses_sum = expenses_data.filter(category=expense, active='a').aggregate(Sum('price'))
        expenses_sum = expenses_sum['price__sum']
        expense_analytics[expense.title] = expenses_sum
    #occupation_analytic
    occupations = Occupation.objects.all()
    person_data = CreatePersonSalaryCost.objects.all().filter(day_added__range=[year_start,day_now])
    occupation_analytics = {}
    for occup in occupations:
        occup_sum = person_data.filter(status='b', person__occupation=occup).aggregate(Sum('value'))
        occup_sum = occup_sum['value__sum']
        occupation_analytics[occup.title] = occup_sum
    logar = Fixed_Costs_item.objects.all()
    #what the fuck is that?
    pagia_id=1
    context = {
        'currency':CURRENCY,
        'date_range':'Από %s εώς %s' % (str(year_start).split(' ')[0], str(day_now).split(' ')[0]),
        'title':title,
        'fixed_costs':fixed_costs,
        'occupations':occupations,
        'log':logar,
        'pagia_id':pagia_id,
        'pagia_exoda':pagia_exoda,
        'bills_all':bills_all,
        'bills_paid':bills_paid,
        'bills_pending':bills_pending,
        'expenses_all':expenses_all,
        'expenses_paid':expenses_paid,
        'expenses_pending':expenses_pending,
        'person_all':person_all,
        'person_paid':person_paid,
        'person_pending':person_pending,
        #analytics
        'bill_analytics':bills_analytics,
        'expenses_analytics':expense_analytics,
        'occupation_analytics':occupation_analytics,
    }
    return render(request,'reports/outcome.html', context)

def checks_reports(request):
    checks = CheckOrder.objects.all().order_by('-date_expire')
    vendors = Supply.objects.all()
    status = CheckOrder.CHOICES
    payment_method = PaymentMethod.objects.all().filter(payment_group__title = 'Bank')
    payment_method_groups = PaymentMethodGroup.objects.all()
    #filters section
    payment_name = None
    vendor_name = None
    status_name = None
    date_pick =None

    if request.POST:
        payment_name = request.POST.getlist('payment_name')
        vendor_name = request.POST.getlist('vendor')
        status_name = request.POST.getlist('status_name')
        date_pick = request.POST.get('date_pick')



        if payment_name:
            checks = checks.filter(place__title__in=payment_name)

        if vendor_name:
            checks = checks.filter(debtor__title__in = vendor_name)

        if status_name:
            checks =checks.filter(status__in =status_name)
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')

            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')

            checks = checks.filter(date_expire__range=[date_start,date_end])


        except:
            date_pick = None


    # get reports after the filters!
    data_per_bank = {}
    if payment_name:
        for payment in payment_name:
            checks_paid = checks.filter(status='b',place__title=payment).aggregate(Sum('value'))
            checks_pending = checks.filter(status='a',place__title = payment).aggregate(Sum('value'))
            data_per_bank[payment.title] = (checks_paid['value__sum'],checks_pending['value__sum'])
    else:
        for payment in payment_method:
            checks_paid = checks.filter(status='b',place=payment).aggregate(Sum('value'))
            checks_pending = checks.filter(status='a',place = payment).aggregate(Sum('value'))
            data_per_bank[payment.title] = (checks_paid['value__sum'],checks_pending['value__sum'])

    checks_paid = checks.filter(status='b').aggregate(Sum('value'))
    checks_paid =checks_paid['value__sum']

    checks_pending = checks.filter(status='a').aggregate(Sum('value'))
    checks_pending = checks_pending['value__sum']





    context = {
        'title':'Checks',
        'checks':checks,
        'status':status,
        'vendors':vendors,
        'payment_method':payment_method,
        'payment_method_groups':payment_method_groups,

        'checks_paid':checks_paid,
        'checks_pending':checks_pending,


        #filters
        'payment_name':payment_name,
        'status_name':status_name,
        'date_pick':date_pick,
        'vendor_name':vendor_name,

        #reports
        'data_per_bank':data_per_bank,

    }
    return render(request, 'reports/check_order_reports.html', context)

def payment_analysis(request):
    title = 'Ροή Πληρωμών'
    #get the day range
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range = date_range.split('-')
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')
        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
    except:
        date_three_months_ago = date_now - relativedelta(months=3)
        date_start = date_three_months_ago
        date_end = date_now
        request.session['date_range'] = '%s-%s'%(date_three_months_ago,date_now)
    #filters
    date_range = '%s -- %s' % (str(date_start).split(' ')[0], str(date_end).split(' ')[0])
    vendors = Supply.objects.all()
    payment_method = PaymentMethod.objects.all()
    payment_method_groups = PaymentMethodGroup.objects.all()
    bills_accounts = Fixed_Costs_item.objects.all()
    occupation_accounts = Occupation.objects.all()
    assets_accounts = Pagia_Exoda.objects.all()
    #collect data for the main table
    deposit_vendor = VendorDepositOrder.objects.filter(day_added__range =[date_start, date_end]).order_by('-day_added')
    order_pay = Order.objects.filter(day_created__range =[date_start, date_end]).order_by('-day_created').exclude(status='p')
    bills = Order_Fixed_Cost.objects.filter(date__range =[date_start, date_end]).filter(active='b').order_by('-date')
    assets = Pagia_Exoda_Order.objects.filter(date__range =[date_start, date_end]).filter(active='b').order_by('-date')
    person = CreatePersonSalaryCost.objects.filter(day_expire__range =[date_start, date_end]).filter(status='b').order_by('-day_expire')
    #create the sum on the total table
    sum_deposit_vendor = deposit_vendor.aggregate(Sum('value'))['value__sum'] if deposit_vendor.aggregate(Sum('value'))['value__sum'] else 0
    sum_per_payment_method ={}
    for ele in payment_method:
        sum = deposit_vendor.filter(payment_method=ele).aggregate(Sum('value'))['value__sum'] if deposit_vendor.filter(payment_method=ele).aggregate(Sum('value'))['value__sum'] else 0
    total_payed_orders = sum_deposit_vendor
    #filters section
    payment_name = None
    vendor_name = None
    date_pick =None
    bills_name = None
    assets_name = None
    person_name = None
    if request.POST:
        payment_name = request.POST.getlist('payment_name')
        vendor_name = request.POST.getlist('vendor_name')
        date_pick = request.POST.get('date_pick')
        assets_name = request.POST.getlist('asset_name')
        person_name = request.POST.getlist('person_name')
        bills_name = request.POST.getlist('bill_name')
        if payment_name:
            deposit_vendor = deposit_vendor.filter(payment_method__title__in=payment_name)
            order_pay = order_pay.filter(payment_method__title__in=payment_name)
            bills =bills.filter(payment_method__title__in=payment_name)
            assets = assets.filter(payment_method__title__in=payment_name)
            person = person.filter(payment_method__title__in=payment_name)
        date_start = None
        date_end = None
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end = datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            deposit_vendor = deposit_vendor.filter(day_added__range=[date_start,date_end])
            order_pay = order_pay.filter(date__range=[date_start,date_end])
            bills = bills.filter(date__range=[date_start,date_end])
            assets = assets.filter(date__range=[date_start,date_end])
            person = person.filter(day_expire__range=[date_start,date_end])
        except:
            date_pick = None
        if vendor_name:
            deposit_vendor = deposit_vendor.filter(vendor__title__in =vendor_name)
            order_pay = order_pay.filter(vendor__title__in= vendor_name)
        else:
            if date_pick or payment_name:
                 deposit_vendor = deposit_vendor.filter(day_added__range=[date_start,date_end])
                 order_pay = order_pay.filter(date__range=[date_start,date_end])
            else:
                deposit_vendor =None
                order_pay = None
        if bills_name:
            bills = bills.filter(category__title__in =bills_name)
        else:
            if date_pick:
                bills = bills.filter(date__range=[date_start,date_end])
            else:
                bills =None
        if assets_name:
            assets = assets.filter(category__title__in = assets_name)
        else:
            if date_pick:
                assets = assets.filter(date__range=[date_start,date_end])
            else:
                assets = None

        if person_name:
            person = person.filter(person__occupation__title__in = person_name)
        else:
            if date_pick:
                person = person.filter(day_expire__range=[date_start,date_end])
            else:
                person = None
    data_per_person=None
    data_per_assets=None
    data_per_bill=None
    data_per_vendor=None
    #get totals on every category
    deposit_vendor_sum = deposit_vendor.aggregate(Sum('value'))['value__sum'] if deposit_vendor.aggregate(Sum('value'))['value__sum'] else 0
    order_pay_sum = order_pay.aggregate(Sum('credit_balance'))['credit_balance__sum'] if order_pay.aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
    bills_sum = bills.aggregate(Sum('credit_balance'))['credit_balance__sum'] if bills.aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
    assets_sum = assets.aggregate(Sum('credit_balance'))['credit_balance__sum'] if assets.aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
    person_sum = person.aggregate(Sum('paid_value'))['paid_value__sum'] if person.aggregate(Sum('paid_value'))['paid_value__sum'] else 0
    #gets total from every category
    list_of_pay_methods = {}
    for payment in payment_method:
        deposit_vendor_payment = deposit_vendor.filter(payment_method__title=payment).aggregate(Sum('value'))['value__sum'] if deposit_vendor.filter(payment_method__title=payment).aggregate(Sum('value'))['value__sum'] else 0
        order_pay_payment = order_pay.filter(payment_method__title=payment).aggregate(Sum('credit_balance'))['credit_balance__sum'] if order_pay.filter(payment_method__title=payment).aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
        bills_sum_payment = bills.filter(payment_method__title=payment).aggregate(Sum('credit_balance'))['credit_balance__sum'] if bills.filter(payment_method__title=payment).aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
        assets_sum_payment = assets.filter(payment_method__title =payment).aggregate(Sum('credit_balance'))['credit_balance__sum'] if assets.filter(payment_method__title =payment).aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
        person_sum_payment = person.filter(payment_method__title =payment).aggregate(Sum('paid_value'))['paid_value__sum'] if person.filter(payment_method__title =payment).aggregate(Sum('paid_value'))['paid_value__sum'] else 0
        total_sum = Decimal(deposit_vendor_payment) + Decimal(order_pay_payment) + Decimal(bills_sum_payment) + Decimal(assets_sum_payment) + Decimal(person_sum_payment)
        list_of_pay_methods[payment.title]= total_sum
        #gets total on specific category
        data_per_vendor ={}
        if vendor_name:
            for ele in vendor_name:
                vendor_deposit_sum = deposit_vendor.filter(vendor__title=ele).aggregate(Sum('value'))['value__sum'] if deposit_vendor.filter(vendor__title=ele).aggregate(Sum('value'))['value__sum'] else 0
                vendor_order_sum = order_pay.filter(vendor__title=ele).aggregate(Sum('total_price'))['total_price__sum'] if order_pay.filter(vendor__title=ele).aggregate(Sum('total_price'))['total_price__sum'] else 0
                data_per_vendor[ele] = (vendor_deposit_sum,vendor_order_sum)
        data_per_bill = {}
        if bills_name:
            for ele in bills_name:
                bills_sum_a = bills.filter(category__title=ele).aggregate(Sum('credit_balance'))['credit_balance__sum'] if bills.filter(category__title=ele).aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
                data_per_bill[ele] = bills_sum_a
        data_per_assets = {}
        if assets_name:
            for ele in assets_name:
                assets_sum_a = assets.filter(category__title=ele).aggregate(Sum('credit_balance'))['credit_balance__sum'] if assets.filter(category__title=ele).aggregate(Sum('credit_balance'))['credit_balance__sum'] else 0
                data_per_assets[ele] = assets_sum_a
        data_per_person ={}
        if person_name:
            for ele in person_name:
                person_sum_a = person.filter(person__occupation__title = ele).aggregate(Sum('paid_value'))['paid_value__sum'] if person.filter(person__occupation__title = ele).aggregate(Sum('paid_value'))['paid_value__sum'] else 0
                data_per_person[ele] = person_sum_a
    context = {
        #filters_update
        'date_pick':date_pick,
        'title':title,
        'vendors':vendors,
        'payment_method':payment_method,
        'payment_method_groups':payment_method_groups,
        'payment_name':payment_name,
        'vendor_name':vendor_name,
        'assets_name':assets_name,
        'person_name':person_name,
        'bill_name':bills_name,
        'bills_account':bills_accounts,
        'assets_accounts':assets_accounts,
        'occupation_account':occupation_accounts,
        #summary data
        'deposit_vendor_sum':deposit_vendor_sum,
        'order_pay_sum':order_pay_sum,
        'bills_sum':bills_sum,
        'assets_sum':assets_sum,
        'person_sum':person_sum,
        'list_of_payment':list_of_pay_methods,
        #summary data after filtering
        'data_per_vendor':data_per_vendor,
        'data_per_bill':data_per_bill,
        'data_per_person':data_per_person,
        'data_per_assets':data_per_assets,
        #table_data
        'bills':bills,
        'person':person,
        'deposit_vendor':deposit_vendor,
        'order_pay':order_pay,
        'assets':assets,
        'date_range':date_range,
        }
    context.update(csrf(request))
    return render(request, 'reports/payment_analysis.html', context)

def log_all(request):
    pagia_id =1
    log_all = Order_Fixed_Cost.objects.all().filter(category__category__title="Λογαριασμοί").order_by('-date')
    #get all bill ber category
    log_all_cat = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    payment_method = PaymentMethod.objects.all()
    #FILTERS
    bill_name = None
    status_name = None
    date_pick = None
    payment_name = None
    if request.POST:
        bill_name = request.POST.get('bill_name')
        status_name = request.POST.get('status_name')
        date_pick = request.POST.get('date_pick')
        payment_name = request.POST.get('payment_name')
        if bill_name:
            log_all = log_all.filter(category__title=bill_name)
        if status_name:
            log_all = log_all.filter(active=status_name)
        if payment_name:
            log_all =log_all.filter(payment_method__title = payment_name)
        if date_pick:
            try:
                date_range = date_pick.split('-')
                date_range[0]=date_range[0].replace(' ','')
                date_range[1]=date_range[1].replace(' ','')
                print(date_range)

                date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')

                log_all = log_all.filter(date__range=[date_start,date_end])
            except:
                date_pick = None
    # i made a dictionary with 2 values, the first is the total order price and the second is the paid value
    # and th third is the pending
    total_orders_per_bill ={}
    for ele in log_all_cat:
        orders = log_all.filter(category__title = ele,).aggregate(Sum('price'))
        pay_orders = log_all.filter(category__title = ele,active ='b').aggregate(Sum('price'))
        pay_order_pending = log_all.filter(category__title = ele,active ='a').aggregate(Sum('price'))
        total_orders_per_bill[ele]=orders['price__sum'],pay_orders['price__sum'],pay_order_pending['price__sum']
    context ={
        'pagia_id':pagia_id,
        'title':'Λογαριασμοί',
        #FILTERS
        'bill_name':bill_name,
        'payment_name':payment_name,
        'log_all_cat':log_all_cat,
        'log_all':log_all,
        'status_name':status_name,
        'date_pick':date_pick,
        'payment_method':payment_method,
        'total_orders_per_bill':total_orders_per_bill,
    }
    return render(request, 'reports/log_main_page.html', context)

def log_all_id(request, dk):
    log_id = Fixed_Costs_item.objects.get(id=dk)
    log_all_cat = Fixed_Costs_item.objects.all().filter(category__title="Λογαριασμοί")
    log_all =Order_Fixed_Cost.objects.all().filter(category__title=log_id.title).order_by('-date')

    context ={
        'log_all_cat':log_all_cat,
        'log_all':log_all,
        'log_id':log_id,
    }
    return render(request, 'reports/log_main_page.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def payroll_report(request):

    day_now = datetime.datetime.now()
    year_start = datetime.datetime(datetime.datetime.now().year,1,1)
    payment_method = PaymentMethod.objects.all()


    payment_category =CategoryPersonPay.objects.all()
    occupation = Occupation.objects.all()
    persons = Person.objects.all()
    all_pay = CreatePersonSalaryCost.objects.all().filter(day_added__range =[year_start,day_now]).order_by('-day_expire')


    date_pick = None
    if request.POST:
        occup = request.POST.get('occup')
        person = request.POST.get('person')
        payment_name = request.POST.get('payment_name')
        date_pick = request.POST.get('date_pick')
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')

            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            all_pay = all_pay.filter(day_expire__range=[date_start,date_end])

        except:
            date_pick=None

        if occup:
            all_pay =all_pay.filter(person__occupation__title=occup)
        if person:
            all_pay = all_pay.filter(person__title = person)
        if payment_name:
            all_pay =all_pay.filter(payment_method__title=payment_name)



    paginator = Paginator(all_pay,20)
    page = request.GET.get('page')
    try:
        pays = paginator.page(page)
    except PageNotAnInteger:
        pays = paginator.page(1)
    except EmptyPage:
        pays  = paginator.page(paginator.num_pages)

    context={
        'title':'Μισθοδοσία',
        'occupation':occupation,
        'persons':persons,
        'all_pay':all_pay,
        'pays':pays,
        'payment_method':payment_method,
        'payment_category':payment_category,
        'date_pick':date_pick,

    }
    return render(request, 'reports/misthodosia_main_page.html', context)

def payroll_analysis(request):
    all_pay = CreatePersonSalaryCost.objects.all()
    occupation = Occupation.objects.all()
    persons = Person.objects.all()
    context = locals()
    return render(request, 'reports/anal_misthodosias.html', context)

def misthodosia_ipal(request,dk):
    occupation = Occupation.objects.all()
    persons = Person.objects.all()
    person =Person.objects.get(id=dk)
    all_pay = CreatePersonSalaryCost.objects.all().filter(person__title=person.title)


    context={
        'title':person.title,
        'occupation':occupation,
        'persons':persons,
        'all_pay':all_pay,

    }
    return render(request, 'reports/misthodosia_main_page.html', context)

def misthodosia_occup(request,dk):
    occup = Occupation.objects.get(id=dk)
    occupation = Occupation.objects.all()
    persons = Person.objects.all()

    all_pay = CreatePersonSalaryCost.objects.all().filter(person__occupation__title = occup.title)


    context={
        'title':occup.title,
        'occupation':occupation,
        'persons':persons,
        'all_pay':all_pay,
    }
    return render(request, 'reports/misthodosia_main_page.html', context)

#---Pagia-Agores--------------------------------------------------------------------------------------------------------------


def agoresEpiskeuesReport(request, dk):
    payment_method = PaymentMethod.objects.all()
    person = PersonMastoras.objects.all()
    all_cate = Pagia_Exoda.objects.all()
    cat = Pagia_Exoda.objects.get(id=dk)
    title ='Πάγια Εξοδα'
    buy_orders = Pagia_Exoda_Order.objects.all().order_by('-date')
    search_pro = request.GET.get('search_pro')
    if search_pro:
        buy_orders =buy_orders.filter(
            Q(title__icontains=search_pro)|
            Q(category__title__icontains =search_pro)|
            Q(person__title__icontains =search_pro)
        ).distinct()

    #filters
    bill_name = None
    date_pick = None
    payment_name = None
    person_name = None

    if request.POST:
        bill_name = request.POST.get('bill_name')
        person_name = request.POST.get('person_name')
        date_pick = request.POST.get('date_pick')
        payment_name = request.POST.get('payment_name')

        if person_name:
            buy_orders = buy_orders.filter(person__title=person_name)

        if bill_name:
            buy_orders = buy_orders.filter(category__title= bill_name)

        if payment_name:
            buy_orders = buy_orders.filter(payment_method__title=payment_name)

        if date_pick:
            try:
                date_range = date_pick.split('-')
                date_range[0]=date_range[0].replace(' ','')
                date_range[1]=date_range[1].replace(' ','')
                print(date_range)

                date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')

                buy_orders = buy_orders.filter(date__range=[date_start,date_end])
            except:
                date_pick = None


    #summary the reports of each category?
    sum_pending_category = {}
    sum_pending_payment_method = {}
    for ele in all_cate:
        orders_pending_sum = buy_orders.filter(category=ele, active='a').aggregate(Sum('price'))
        keep_data=[]
        for pay in payment_method:
            pay_pending = buy_orders.filter(category=ele,payment_method=pay,active='b').aggregate(Sum('price'))
            pay_paid = buy_orders.filter(category=ele,payment_method=pay, active='a').aggregate(Sum('price'))
            keep_data.append([pay.title,pay_pending['price__sum'],pay_paid['price__sum']])
        sum_pending_category[ele] = keep_data

    context ={
        'title':title,
        'buy_orders':buy_orders,
        'cat':cat,
        'all_cate':all_cate,
        'person':person,
        'payment_method':payment_method,

        'sum_pending_category':sum_pending_category,
    }
    return render(request, 'reports/pagia_agores.html',context)


def partners(request):
    all_cate = Pagia_Exoda.objects.all()
    title = 'Εξωτερικοί συνεργάτες'
    persons = PersonMastoras.objects.all()
    pagia_id=1
    search_pro = request.GET.get('search_pro')
    if search_pro:
        persons =persons.filter(
            Q(title__icontains=search_pro)|
            Q(phone__icontains =search_pro)|
            Q(phone1__icontains =search_pro)|
            Q(occupation__icontains = search_pro)
        ).distinct()

    context = locals()
    return render(request, 'reports/exoterikoi_si.html',context)




