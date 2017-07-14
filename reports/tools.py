from products.models import SizeAttribute
from django.db.models import Q


def warehouse_filters(request, products,):
    category_name = []
    vendor_name = []
    color = []
    discount_name = None
    qty_name = None
    if request.GET:
        category_name = request.GET.getlist('category_name')
        vendor_name = request.GET.getlist('vendor_name')
        site_status = request.GET.get('site_status')
        color = request.GET.getlist('color_name')
        size_name = request.GET.getlist('size_name')
        discount_name = request.GET.get('discount_name')
        qty_name = request.GET.get('qty_name')
        if qty_name:
            products = products.filter(qty__gt=0)
        if discount_name:
            products.filter(price_discount__gt=0)
        if color:
            products = products.filter(color__title__in=color)
        if category_name:
            products = products.filter(category__id__in=category_name)
        if vendor_name:
            products = products.filter(supplier__id__in=vendor_name)
        if site_status:
            products = products.filter(status__in=site_status)
        if size_name:
            size_attr = SizeAttribute.objects.filter(product_related__in=products, title__id__in=size_name)
            products_with_size = [ele.product_related.id for ele in size_attr]
            products = products.filter(id__in=products_with_size)
    if request.POST:
        query = request.POST.get('search_pro')
        if query:
            products = products.filter(
                Q(title__icontains=query)|
                Q(category__title__icontains=query) |
                Q(supplier__title__icontains=query) |
                Q(order_code__icontains=query)
            ).distinct()
    return [products, category_name, vendor_name, color, discount_name, qty_name]