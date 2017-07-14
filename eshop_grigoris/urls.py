"""eshop_grigoris URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from tools.views import set_up_database,clear_sessions
from mysite.views import *
from mysite.views_admin import print_order
from cart.views import remove_item_from_cart,add_to_cart
from products.views import welcome_page
from django.contrib.sitemaps.views import sitemap
from site_maps.views import *

sitemaps = {
    'product': ProductSitemap,
}

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #site urls
    url(r'^$', view=homepage),
    url(r'^product/(?P<slug>[-\w]+)/$', view=product_page, name='product_page'),
    url(r'^ajax-search/$', view=ajax_results, name='ajax_search'),
    url(r'^page-results/$', view=page_results, name='page_results'),
    url(r'^προσφορές/$', view=offers_product_page, name='offers_page'),
    url(r'^register/$', view=register_page, name='register_page'),
    url(r'^costumer-page/$', view=costumer_page, name='costumer_page'),
    url(r'^costumer-page-ask/$', view=costumer_ask_page, name='costumer_ask_page'),
    url(r'^costumer-page-order/$', view=costumer_page_order, name='costumer_page_order'),
    url(r'^costumer-order/(?P<order_id>.*)/$', view=costumer_specific_order, name='costumer_order'),
    url(r'^contact/$', view=contact_page, name='contact_page'),
    url(r'^faq/$', view=faq_page, name='faq_page'),
    url(r'^info-eshop/$', view=informations_page, name='info_page'),
    url(r'^my-account/$', view=my_account, name='my_account'),
    url(r'^category/(?P<slug>[-\w]+)/$', view=category_site, name='category_site'),
    url(r'^brand/(?P<slug>[-\w]+)/$', view=brand_page_products, name='brand_site'),
    url(r'^change-show-product/(?P<dk>\d+)/$', view=change_show_product_number, name='change_show_product'),
    url(r'^site/clear-session/(?P<slug>[-\w]+)/$', view=my_site_clear_session, name='my_site_clear_session'),
    url(r'^καλάθι-αγορών/$', view=basket, name='basket'),
    url(r'^cart_html/$', view=cart_html,),
    url(r'^add-to-cart/(?P<dk>\d+)/$', view=add_to_cart, name='cart_item_add'),
    url(r'^cart-item-delete/(?P<dk>\d+)/$', view=remove_item_from_cart, name='cart_item_delete'),
    url(r'^checkout/$', view=checkout, name='checkout'),
    url(r'^checkout-review/$', view=checkout_review, name='checkout_review'),
    #url(r'^checkout/$', view=checkout, name='checkout'),
    #url(r'^checkout/$', view=checkout, name='checkout'),
    #print statements
    #warehouse urls
    url(r'^home/$', view=welcome_page, name='welcome_page'),
    url(r'^accounts/',include('account.urls')),
    url(r'^αποθήκη/',include('products.urls')),
    url(r'^πληρωμές-εισπράξεις/',include('transcations.urls')),
    url(r'^PoS/',include('PoS.urls')),
    url(r'^reports/',include('reports.urls')),
    url(r'^blog/',include('blog.urls')),
    url(r'^site/',include('mysite.urls')),
    # that url setup the database, comment it after the use
    url(r'^database/',view=set_up_database),
    url(r'^clear-sessions/',view=clear_sessions),
    #url(r'^sitemap\.xml', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

