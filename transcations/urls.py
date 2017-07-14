from django.conf.urls import url, include
from .views import *



urlpatterns = [
    url(r'^$',view=homepage),
    url(r'^αποπληρωμές-τιμολογίων/$',view=pay_order_section, name='order_pay_section'),
    url(r'^αποπληρωμές-τιμολογίων/δόσεις/$',view=orders_in_dept),
    url(r'^αποπληρωμές-τιμολογίων/δόσεις/(?P<dk>\d+)/$',view=orders_in_dept_id),
    url(r'^αποπληρωμές-τιμολογίων/(?P<dk>\d+)/$',view=pay_order, name='pay_order'),
    url(r'^αποπληρωμές-τιμολογίων/προκαταβολές/(?P<dk>\d+)/$',view=pay_order_from_deposit),
    url(r'^αποπληρωμές-τιμολογίων/αποπληρωμένα/$',view=pay_orders_fullpayment, name='order_full_pay'),
    url(r'^αποπληρωμές-τιμολογίων/δόσεις/ιστορικό/(?P<dk>\d+)/$',view=orders_history_id),

    url(r'^πάγια-έξοδα/$',view=fixed_costs),
    url(r'^πάγια-έξοδα/λογαριασμοί/(?P<dk>\d+)/$',view=fixed_costs_log_id, name='specific_bill'),
    url(r'^πάγια-έξοδα/λογαριασμοί/κατηγορία/προσθήκη/$',view=create_new_log_cat),


    url(r'^πάγια-έξοδα/λογαριασμοί/προσθήκη/(?P<dk>\d+)/$',view=create_log_order),
    url(r'^πάγια-έξοδα/λογαριασμοί/πληρωμή/(?P<dk>\d+)/(?P<pk>\d+)/edit/$',view=edit_log_id),
    url(r'^πάγια-έξοδα/λογαριασμοί/πληρωμή/(?P<dk>\d+)/(?P<pk>\d+)/$',view=pay_log_id),

    url(r'^πάγια-έξοδα/προσωπικό/(?P<dk>\d+)/$',view=fixed_cost_ppl_id),
    url(r'^πάγια-έξοδα/προσωπικό/προσθήκη-κατηγορίας/$',view=add_occupation),
    url(r'^πάγια-έξοδα/προσωπικό/edit/(?P<dk>\d+)/(?P<pk>\d+)$',view=edit_ppl_id),


    url(r'^πάγια-έξοδα/προσωπικό/απενεργοποιημένο/(?P<dk>\d+)/$',view=deactivated_ppl),
    url(r'^πάγια-έξοδα/προσωπικό/energy/(?P<dk>\d+)/(?P<pk>\d+)/$',view=activate_ppl),
    url(r'^πάγια-έξοδα/προσωπικό/d-energy/(?P<dk>\d+)/(?P<pk>\d+)/$',view=deactive),

    url(r'^πάγια-έξοδα/προσωπικό/προσθήκη/(?P<dk>\d+)/$',view=create_fixed_cost_ppl),
    url(r'^πάγια-έξοδα/προσωπικό/υπόλοιπο/(?P<dk>\d+)/$',view=pay_remaining, name='working_ppl_id'),
    url(r'^πάγια-έξοδα/προσωπικό/υπόλοιπο/(?P<dk>\d+)/(?P<pk>\d+)/$',view=pay_remaining_id),

    url(r'^πάγια-έξοδα/προσωπικό/(?P<dk>\d+)/(?P<pk>\d+)/$',view=add_pay_order_to_person),
    url(r'^πάγια-έξοδα/προσωπικό/υπόλοιπο/επεξεργασία/(?P<dk>\d+)/(?P<pk>\d+)/(?P<ok>\d+)/$', view=edit_people_order),

    url(r'^πάγια-έξοδα/(?P<dk>\d+)/$',view=pagia_exoda),
    url(r'^πάγια-έξοδα/(?P<dk>\d+)/προσθήκη/$',view=pagia_exoda_create_order),
    url(r'^πάγια-έξοδα/(?P<dk>\d+)/add-company/$',view=pagia_exoda_create_person),
    url(r'^πάγια-έξοδα/πληρωμή/(?P<dk>\d+)/(?P<pk>\d+)/$',view=pagia_exoda_pay_order),
    url(r'^πάγια-έξοδα/επεξεργασία/(?P<dk>\d+)/(?P<pk>\d+)/$',view=pagia_exoda_edit_order),






]