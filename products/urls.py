from django.conf.urls import url
from .views import *
from tools.views import warehouse_product_table_order, warehouse_vendor_table_order, warehouse_table_order, clear_session_create_pro
from .views_tools import *
from .views_products import *
from .views_orders import *
from .api.views import *


urlpatterns=[
    url(r'^$', view=homepage),
    url(r'^welcome-page-paid/$', view=welcome_page_paid_section, name='welcome_page_paid'),
    url(r'^welcome-warehouse/$', view=welcome_page_warehouse, name='welcome_page_warehouse'),
    url(r'^προιόντα/$', view=products, name='products'),
    url(r'^προιόντα/ajax-search/$', view=ajax_product_search),
    url(r'^προιόντα/duplicate/(?P<dk>\d+)/$', view=create_duplicated_product, name='duplicate_product'),
    url(r'^προιόντα/activate/(?P<dk>\d+)/$', view=activate_deactivate_product),
    url(r'^προιόντα/δημιουργία/$', view=create_product, name='create_product'),
    url(r'^προιόντα/brand/δημιουργία/(?P<dk>\d+)/$', view=create_brand, name='create_brand_id'),
    url(r'^προιόντα/brand/δημιουργία/$', view=create_brand, name='create_brand'),
    url(r'^προιόντα/table-order-by/(?P<text>\w+)/$', view=warehouse_product_table_order),
    url(r'^προιόντα/add-characteristics/(?P<dk>\d+)/$', view=product_add_characteristics, name='add_characteristics'),
    url(r'^προιόντα/επεξεργασία/vendoras/', view=create_vendor_from_product),
    url(r'^προιόντα/επεξεργασία/category/', view=create_category_from_product),
    url(r'^προιόντα/επεξεργασία/site-category/(?P<dk>\d+)/', view=create_category_site_from_product, name='create_cat_site_pro'),
    url(r'^προιόντα/επεξεργασία/site-category/', view=create_category_site_from_product, name='create_cat_site_pro_alt'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/$', view=edit_product, name='edit_product'),
    url(r'^προιόντα/επεξεργασία/related-ajax/$', view=ajax_related_products, name='ajax_edit_related'),
    url(r'^προιόντα/επεξεργασία/related-ajax/(?P<dk>\d+)/(?P<pk>\d+)/$', view=add_or_remove_related_products, name='ajax_add_related'),
    url(r'^προιόντα/επεξεργασία/related-ajax/(?P<dk>\d+)/delete/(?P<pk>\d+)/$', view=delete_related_product, name='ajax_delete_related'),
    url(r'^προιόντα/επεξεργασία/color-ajax/$', view=ajax_color_products, name='ajax_edit_color'),
    url(r'^προιόντα/επεξεργασία/color-ajax/(?P<dk>\d+)/(?P<pk>\d+)/$', view=add_or_remove_color_products, name='ajax_add_color'),
    url(r'^προιόντα/επεξεργασία/color-ajax/(?P<dk>\d+)/delete/(?P<pk>\d+)/$', view=delete_color_product, name='ajax_delete_color'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/νούμερα/$', view=edit_product_create_size, name='edit_product_choose_size'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/νούμερα/επεξεργασία/$', view=edit_product_edit_number, name='edit_product_edit_size'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/νούμερα/διαγραφή/$', view=edit_product_delete_number, name='edit_product_delete_size'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/add-photo/$', view=add_photo_to_product, name='add_photo_to_product'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/delete-photo/$', view=delete_photo_from_product, name='delete_photo_from_product'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/edit-photo/$', view=edit_photo_from_product, name='edit_photo_from_product'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/add-characteristic/(?P<type>[-\w]+)/$', view=add_characteristic_from_product, name='add_char_from_product'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/(?P<pk>\d+)/edit-characteristic/$', view=edit_char_from_product, name='edit_char_from_product'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/(?P<pk>\d+)/edit-characteristic/color$', view=edit_char_from_color_attr, name='edit_char_from_color_attr'),
    url(r'^προιόντα/επεξεργασία/(?P<dk>\d+)/delete-characteristic/$', view=delete_char_from_product, name='delete_char_from_product'),
    url(r'^προιόντα/clear-sessions/$',view=clear_session_create_pro),
    url(r'^προιόντα/δημιουργία/delete-size/(?P<dk>\d+)/(?P<pk>\d+)/$',view=delete_size),
     url(r'^προιόντα/δημιουργία/delete/(?P<dk>\d+)/$', view=delete_product, name='product_delete'),


    url(r'^προμηθευτές/$', view=vendors, name='vendors'),
    url(r'^προμηθευτές/ajax-search/$', view=ajax_vendors),
    url(r'^προμηθευτές/table-order-by/(?P<text>\w+)/$', view=warehouse_vendor_table_order),
    url(r'^προμηθευτές/δημιουργία/$', view=create_vendor , name='create_vendor'),
    url(r'^προμηθευτές/επεξεργασία/(?P<dk>\d+)/$', view=edit_vendor, name='edit_vendor'),

    url(r'^προμηθευτές/διαχείρηση-επιταγών/$',view=check_orders_management, name='check_order_management'),
    url(r'^προμηθευτές/διαχείρηση-επιταγών/(?P<dk>\d+)/$',view=edit_check_order),

    url(r'^προμηθευτές/προκαταβολή/(?P<dk>\d+)/$', view=vendor_deposit_order),
    url(r'^προμηθευτές/επιταγή/(?P<dk>\d+)/$', view=vendor_check_order),
    url(r'^προμηθευτές/επιταγή/(?P<dk>\d+)/είσπραξη/$', view=payment_check),

    url(r'^τιμολόγια/$', view=orders, name='warehouse_order'),
    url(r'^τιμολόγια/ajax-search/$', view=ajax_orders),
    url(r'^τιμολόγια/νέο/$', view=create_order, name='create_order'),
    url(r'^τιμολόγια/(?P<dk>\d+)/$', view=edit_order, name='edit_order'),
    url(r'^τιμολόγια/(?P<dk>\d+)/delete/$', view=delete_order, name='delete_order'),
    url(r'^τιμολόγια/προμηθευτής/$', view=create_vendor_from_order),

    url(r'^pre-order-section/$', view=pre_order_section, name='pre_order_section'),
    url(r'^pre-order-section/create/$', view=pre_order_create, name='pre_order_create'),
    url(r'^pre-order-section/create-new-item/$', view=pre_order_create_new_item, name='pre_order_create_new_item'),
    url(r'^pre-order-section/delete-new-item/(?P<dk>\d+)/$', view=pre_order_delete_new_item, name='pre_order_delete_new_item'),
    url(r'^pre-order-section/edit-new-item/(?P<dk>\d+)/$', view=pre_order_edit_new_item, name='pre_order_edit_new_item'),
    url(r'^pre-order-section/edit/(?P<dk>\d+)/$', view=pre_order_edit_item, name='pre_order_edit_item'),
    url(r'^pre-order-section/delete/(?P<dk>\d+)/$', view=pre_order_delete_item, name='pre_order_delete_item'),
    url(r'^pre-order-section/pre-order-to-order/(?P<dk>\d+)/$', view=create_order_from_pre_order_statement, name='pre_order_create_order'),

    url(r'^pre-order-section/order-statement/(?P<dk>\d+)/$', view=pre_order_show_statement, name='pre_order_show_statement'),
    url(r'^pre-order-section/order-statement/edit/(?P<dk>\d+)/(?P<pk>\d+)/$', view=pre_order_show_statement_edit_product, name='pre_order_statement_edit_product'),
    url(r'^pre-order-section/order-statement/edit-new/(?P<dk>\d+)/(?P<pk>\d+)/$', view=pre_order_show_statement_edit_new_product, name='pre_order_statement_edit_new_product'),

    url(r'^εργαλεία/table-order-by/(?P<text>\w+)/(?P<dk>\d+)/$',view=warehouse_table_order),
    url(r'^εργαλεία/product-checkbox-options/$',view=product_checkbox_options),

    url(r'^εργαλεία/$',view=tools, name='tools'),
    url(r'^εργαλεία/χαρακτηριστικά/$', view=tools_characteristics, name='tools_char'),
    url(r'^εργαλεία/χαρακτηριστικά/δημιουργία/$', view=tools_create_char, name='tools_char_create'),
    url(r'^εργαλεία/χαρακτηριστικά/δημιουργία/(?P<dk>\d+)/$', view=tools_edit_char, name='tools_char_edit'),
    url(r'^εργαλεία/χαρακτηριστικά/διαγραφή-χαρακτηριτικού/(?P<dk>\d+)/$', view=tools_delete_char, name='tools_char_delete'),

    url(r'^εργαλεία/χαρακτηριστικά-values/δημιουργία/$', view=tools_create_char_val, name='tools_char_val_create'),
    url(r'^εργαλεία/χαρακτηριστικά-values/δημιουργία/(?P<dk>\d+)/$', view=tools_edit_char_val, name='tools_char_val_edit'),
    url(r'^εργαλεία/χαρακτηριστικά-values/διαγραφή-χαρακτηριτικού/(?P<dk>\d+)/$', view=tools_delete_char_val, name='tools_char_val_delete'),

    url(r'^εργαλεία/payment_group/(?P<dk>\d+)$', view=edit_payment_group),
    url(r'^εργαλεία/payment/(?P<dk>\d+)$', view=edit_payment),
    url(r'^εργαλεία/payment/brand/$', view=tools_add_edit_brand, name='tools_add_brand'),
    url(r'^εργαλεία/payment/brand/(?P<dk>\d+)/$', view=tools_add_edit_brand, name='tools_edit_brand'),

    url(r'^εργαλεία/category/$',view=tools_new_category),
    url(r'^εργαλεία/category/(?P<dk>\d+)$',view=tools_edit_category),
    url(r'^εργαλεία/category-site/$',view=tools_new_category_site, name='tools_cat_site_new'),
    url(r'^εργαλεία/category-site/(?P<dk>\d+)$',view=tools_edit_category_site, name='tools_cat_site_edit'),

    url(r'^εργαλεία/(?P<dk>\d+)/$',view=activate_or_deactive_color),
    url(r'^εργαλεία/edit/(?P<dk>\d+)/$',view=tools_edit_color),
    url(r'^εργαλεία/size/(?P<dk>\d+)/$',view=activate_deactivate_size),
    url(r'^εργαλεία/size/edit/(?P<dk>\d+)/$',view=tools_edit_size),

    url(r'^εργαλεία/αλλαγή-ποσότητας/δημιουργία/$', view=tools_change_order),
    url(r'^εργαλεία/αλλαγή-ποσότητας/(?P<dk>\d+)/$', view=tools_change_qty, name='tools_change_qty_id'),
    url(r'^εργαλεία/αλλαγή-ποσότητας/(?P<dk>\d+)/(?P<pk>\d+)$', view=tools_grab_qty, name='tools_change_grab_qty'),
    url(r'^εργαλεία/αλλαγή-ποσότητας/size/(?P<dk>\d+)/(?P<pk>\d+)$', view=tools_grab_size, name='tools_change_qty_size'),
    url(r'^εργαλεία/discount/$', view=tools_discount_page, name='tools_discount'),
    url(r'^εργαλεία/discount/(?P<dk>\d+)/$', view=discount_order_specific, name='tools_discount_specific'),

    url(r'^τιμολόγια/DOY/$', view=create_taxes_city),
    url(r'^τιμολόγια/επεξεργασία/(?P<dk>\d+)/$', view=order_edit_id, name='order_edit_main'),

    #add on order items urls
    url(r'^τιμολόγια/check/(?P<dk>\d+)/(?P<pk>\d+)/$', view=add_product_to_order, name='add_product_order'),
    url(r'^τιμολόγια/check/(?P<dk>\d+)/(?P<pk>\d+)/size/$', view=add_product_with_sizes, name='add_product_order_size'),
    url(r'^τιμολόγια/επεξεργασία-προϊόντος/(?P<dk>\d+)/(?P<pk>\d+)/$', view=edit_product_from_order),
    url(r'^τιμολόγια/διαγραφή/(?P<dk>\d+)/$', view=delete_order, name='delete_order'),
    url(r'^τιμολόγια/(?P<dk>\d+)/επεξεργασία/$', view=order_edit),
    url(r'^τιμολόγια/διαγραφή-προιόντος/(?P<dk>\d+)/$',view=delete_order_item),

    url(r'^costumers/$', view=costumers_section, name='warehouse_costumers'),
    url(r'^costumers/new-costumer/$', view=costumers_new, name='warehouse_costumers_new'),
    url(r'^costumers/edit/(?P<dk>\d+)/$', view=edit_costumer, name='warehouse_costumers_edit'),

    url(r'^api/products/$', ProductListAPIView.as_view(), name='api_products'),
    url(r'^api/products/create/$', ProductCreateAPIView.as_view(), name='api_product_create'),
    url(r'^api/products/(?P<pk>[-\w]+)/$', ProductUpdateAPIView.as_view(), name='api_product_detail'),
    #url(r'^api/posts/update/(?P<slug>[-\w]+)/$', PostUpdateAPIView.as_view(), name='api_post_update'),
    #url(r'^api/posts/delete/(?P<slug>[-\w]+)/$', PostDe
]




