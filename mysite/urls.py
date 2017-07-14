from django.conf.urls import url, include
from tools.views import clear_sessions_site_admin_orders
from .views_admin import *


urlpatterns = [
    url(r'^$', view=site_admin, name='site_admin'),
    url(r'^message-section/$', view=site_show_messages, name='site_msg'),
    url(r'^order_management/$', view=orders_management, name='orders_admin'),
    url(r'^order_management/new/$', view=new_eshop_orders, name='new_orders_admin'),
    url(r'^order_management/in-progress/$', view=in_progress_eshop_orders, name='in_progress_orders_admin'),
    url(r'^order_management/done/$', view=done_eshop_orders, name='done_orders_admin'),
    url(r'^order_management/order/(?P<dk>\d+)/$', view=eshop_order, name='eshop_order'),
    url(r'^order_management/order/edit/(?P<dk>\d+)/$', view=eshop_order_full_edit, name='eshop_order_full_edit'),
    url(r'^order_management/order-item-is-find/(?P<dk>\d+)//(?P<pk>\d+)$', view=order_item_is_find, name='order_item_is_find'),
    url(r'^order_management/order-item-change-status/(?P<dk>\d+)/(?P<pk>\d+)$', view=eshop_change_status, name='eshop_change_status'),
    url(r'^order_management/order-item-shipping-status/(?P<dk>\d+)/(?P<pk>\d+)$', view=eshop_change_shipping, name='eshop_change_shipping'),
    url(r'^order_management/order-item-payment-status/(?P<dk>\d+)/(?P<pk>\d+)$', view=eshop_change_payment, name='eshop_change_payment'),
    url(r'^order_management/products_order/$', view=products_in_progress, name='products_in_pro'),
    url(r'^blog/$', view=site_blog, name='blog_admin'),
    url(r'^blog/create/$', view=site_blog_create, name='blog_admin_create'),
    url(r'^blog/edit/(?P<dk>\d+)/$', view=site_blog_edit, name='blog_admin_edit'),
    url(r'^blog/create/tag/$', view=site_blog_create_tag, name='tag_admin_create'),
    url(r'^blog/edit/tag/(?P<dk>\d+)/$', view=site_blog_edit_tag, name='tag_admin_edit'),
    url(r'^blog/create/cat/$', view=site_blog_create_cat, name='cat_admin_create'),
    url(r'^blog/edit/cat/(?P<dk>\d+)/$', view=site_blog_edit_cat, name='cat_admin_edit'),
    url(r'^control/$', view=site_control, name='site_control'),
    url(r'^control/banners/$', view=site_control_banners, name='site_control_banners'),
    url(r'^control/newsletter/$', view=site_newsletter, name='site_control_newsletter'),
    url(r'^control/contact/$', view=site_contact_info, name='site_control_contact'),
    url(r'^print/(?P<dk>\d+)/$', view=print_order, name='print_order'),

    #clear_session
    url(r'^order_management/clear-sessions/$', view=clear_sessions_site_admin_orders, name='clear_session_site_orders'),

    ]
