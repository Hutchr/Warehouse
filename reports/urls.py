from django.conf.urls import url
from .views import *
from .views_warehouse import *
from .views_outcome import *
from tools.views import clear_sessions_reports_income, clear_sessions_reports_products


urlpatterns = [
    url(r'^$',view=homepage, name='reports'),
    url(r'warehouse/$', view=warehouse),
    url(r'products/$', view=products, name='reports_products'),
    url(r'products-flow/$', view=products_movements, name='products_flow'),
    url(r'products/ajax-search/$',view=ajax_reports_product_info),
    url(r'products/clear-sessions/$',view=clear_sessions_reports_products, name='session_product_rep'),
    url(r'products/cat/(?P<dk>\d+)/$',view=products_category, name='product_category_id'),
    url(r'products/vend/(?P<dk>\d+)/$',view=products_vendors),
    url(r'products/(?P<dk>\d+)/$',view=product_id, name='info_product_id'),
    url(r'category-report/$', view =category_report, name='category_report'),
    url(r'vendors/$',view=vendors),
    url(r'vendors/(?P<dk>\d+)/$',view=vendors_id, name='vendor_info'),
    url(r'vendors/(?P<dk>\d+)/add/(?P<pk>\d+)/$' ,view=add_to_pre_order, name='vendor_info_add_preorder'),
    url(r'vendors-doy/(?P<dk>\d+)/$',view=vendors_per_doy),
    url(r'orders/$',view=orders),
    url(r'orders/(?P<dk>\d+)/$',view=order_id, name='report_order_id'),
    url(r'orders/reset-payments/(?P<dk>\d+)/$',view=reports_order_reset_payments, name='report_order_edit'),
    url(r'orders-per-vendor/(?P<dk>\d+)/$',view=orders_per_category),
    url(r'outcome/$', view=outcome),
    url(r'outcome/payment-analysis/$',view=payment_analysis),
    url(r'outcome/logariasmoi/$',view=log_all),
    url(r'outcome/logariasmoi/(?P<dk>\d+)/$',view=log_all_id),
    url(r'outcome/μισθοδοσία/$',view=payroll_report),
    url(r'outcome/επιταγές/$',view=checks_reports),
    url(r'outcome/μισθοδοσία/analitika/$', view=payroll_analysis),
    url(r'outcome/μισθοδοσία/ipal/(?P<dk>\d+)/$',view=misthodosia_ipal),
    url(r'outcome/μισθοδοσία/ocup/(?P<dk>\d+)/$',view=misthodosia_occup),
    url(r'outcome/pagia-agores/(?P<dk>\d+)/$',view=agoresEpiskeuesReport),
    url(r'outcome/pagia-agores/exoterikoi-synergates/$',view=partners),
    url(r'income/$',view=reports_income, name='reports_income'),
    url(r'income-flow-items/$', view = sell_items_flow, name='sell_item_flow'),
    url(r'costumer-report-balance/$', view = costumers_accounts_report, name='costumers_reports'),
    url(r'costumer-report-balance/(?P<dk>\d+)/$', view = specific_costumer_account, name='specific_costumer_report'),
    url(r'income/clear-sessions/$', view=clear_sessions_reports_income),
    url(r'income/product/(?P<dk>\d+)/$', view=reports_specific_order, name='reports_specific_order'),
    url(r'isologismos/$',view=isologismos,),
    url(r'balance-sheet-estimate/$',view=balance_sheet_estimate,),
    url(r'balance-sheet-estimate/current-month/$',view=balance_sheet_estimate_current_month,),
    url(r'balance-sheet-estimate/three-months/$',view=balance_sheet_estimate_current_three_months,),
    url(r'setting/', view =report_settings, name='report_settings'),
    ]
