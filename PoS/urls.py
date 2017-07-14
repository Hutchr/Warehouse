from django.conf.urls import url
from .views import *
from .views_eshop import *




urlpatterns =[
    url(r'^$', view=homepage, name='pos_section'),
    url(r'lianiki/$', view=retail_options),
    url(r'lianiki/edit/(?P<dk>\d+)/$', view=pos_edit_order, name='pos_edit_order'),
    url(r'lianiki/delete/(?P<dk>\d+)/$', view=delete_order),
    url(r'lianiki/create-return/$', view=create_return_order),


    url(r'destroy-order/$', view=destroy_order),
    url(r'destroy-order/(?P<dk>\d+)/$', view=destroy_order_products, name='pos_destroy_order'),
    url(r'destroy-order/(?P<dk>\d+)/(?P<pk>\d+)auto//$', view=destroy_order_item_auto, name='destroy_auto'),
    url(r'destroy-order/(?P<dk>\d+)/(?P<pk>\d+)/$', view=destroy_order_item_id, name='destroy_item'),
    url(r'destroy-order/(?P<dk>\d+)/(?P<pk>\d+)/delete/$', view=destroy_order_item_delete),
    url(r'destroy-order/(?P<dk>\d+)/(?P<pk>\d+)/edit/$', view=destroy_order_item_edit),

    url(r'return-order/$', view=create_return_order, name='create_return_order'),

    url(r'lianiki/new-order/$', view=new_retail_order),
    url(r'lianiki/order/activate-deactivate-taxes/(?P<dk>\d+)/', view=activate_deactivate_taxes, name='activate_deactivate_taxes'),
    url(r'lianiki/order/delete/(?P<dk>\d+)/', view=delete_order, name='delete_retail_order'),
    url(r'lianiki/order/(?P<dk>\d+)/$', view=retail_main_page, name='retail_order_section'),
    url(r'lianiki/order/new-costumer/(?P<dk>\d+)/$', view=pos_create_new_costumer, name='pos_create_costumer'),
    url(r'lianiki/order/(?P<dk>\d+)/(?P<pk>\d+)/$', view=retail_category_page),
    url(r'retail/order/choose-size/(?P<dk>\d+)/(?P<pk>\d+)/$', view=retail_choose_size_page, name='retail_choose_size'),
    url(r'lianiki/order/auto-add/(?P<dk>\d+)/(?P<pk>\d+)/$', view=add_product_to_order_auto, name='retail_auto_add'),
    url(r'lianiki/order/(?P<dk>\d+)/(?P<pk>\d+)/add/$', view=retail_add_product, name='retail_add'),



    url(r'lianiki/order/(?P<dk>\d+)/(?P<pk>\d+)/edit/$', view=retail_edit_order_item),
    url(r'lianiki/order/(?P<dk>\d+)/(?P<pk>\d+)/delete/$', view=retail_delete_order_item),
    url(r'lianiki/order/(?P<dk>\d+)/pay/$', view=lianiki_order_pay_not_complete),
    url(r'lianiki/order/(?P<dk>\d+)/closed/$', view=lianiki_order_closed),


    url(r'eshop/$', view=eshop_homepage),
    url(r'eshop/new-order/$', view=eshop_new_order, name='eshop_new_order'),
    url(r'eshop/add-costumer/(?P<dk>\d+)/$', view=eshop_add_costumer_account, name='eshop_add_costumer_account'),
    url(r'eshop/new-order/submit/$', view=create_eshop_order, name='eshop_new_order_submit'),
    url(r'eshop/new-order/add-product/(?P<dk>\d+)/$', view=eshop_add_product, name='eshop_add_product_auto'),
    url(r'eshop/new-order/delete/(?P<dk>\d+)/$', view=eshop_delete_product, name='eshop_delete_product'),



    url(r'stats/$',view=total_stats),
    url(r'admin/$',view=admin_section),


    url(r'orders_management/$',view=orders_management, name='orders_management'),
    url(r'orders_management/details/(?P<dk>\d+)/$',view=orders_management_details, name='orders_management_details'),
    url(r'orders_management/(?P<dk>\d+)/(?P<pk>\d+)/$',view=orders_management_change, name='orders_management_change'),
    url(r'orders_management/(?P<dk>\d+)/item-change/$',view=orders_management_product_change, name='orders_management_product_change'),


    ]
