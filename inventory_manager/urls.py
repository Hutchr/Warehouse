from django.conf.urls import url, patterns


urlpatterns =[
    url(r"^/$", "inventory_manager.views.homepage",name='inventory'),
    url(r"^vendors/$",'inventory_manager.views.vendors',name="vendors"),
    url(r'vendors/edit/$','inventory_manager.views.vendors_edit', name="edit_vendors"),
    url(r'vendors/edit/(?P<dk>\d+)/$','inventory_manager.views.vendors_edit_id', name="edit_vendor_id"),
    url(r'vendors/details/$','inventory_manager.views.vendors_details', name="vendor_details"),
    url(r'vendors/details/(?P<dk>\d+)/$','inventory_manager.views.vendor_analytics', name="vendor_ana"),

    url(r'^products/$','inventory_manager.views.products', name="products"),

    url(r'^products/vendor/(?P<dk>\d+)/$','inventory_manager.views.edit_product_vendor', name="edit_products_vendor"),

    url(r'^products/edit/$','inventory_manager.views.edit_product', name="edit_product"),
    url(r'^products/edit/category/(?P<dk>\d+)/$','inventory_manager.views.edit_products_category', name="edit_product_category"),
    url(r'^products/edit/(?P<dk>\d+)/$','inventory_manager.views.edit_product_id', name="edit_product_id"),


    url(r'^movements/$','inventory_manager.views.movements',name ="movements"),
    url(r'^movements/new_order/add_product/$','inventory_manager.views.add_product_to_order',name ="new_order_add_product"),
    url(r'^movements/edit_orders/vendor/(?P<dk>\d+)/$','inventory_manager.views.edit_order_vendor',name ="edit_order_vendor"),
    url(r'^movements/edit_orders/vendor/edit/(?P<dk>\d+)/$','inventory_manager.views.edit_order_id',name ="edit_order_id"),
    url(r'^movements/edit_orders/item_order/(?P<dk>\d+)/$','inventory_manager.views.edit_item_order_id',name ="edit_itemorder_id"),








    url(r'^movements/all_orders/$','inventory_manager.views.all_orders',name ="all_orders"),
    url(r'^movements/all_orders/vendor//$','inventory_manager.views.all_orders_vendor',name ="all_orders_vendor"),
    url(r'^movements/all_orders/(?P<dk>\d+)/$','inventory_manager.views.all_order_id',name ="all_order_id"),
    url(r'^movements/all_orders/edit_order/$','inventory_manager.views.edit_order',name ="edit_order"),












]