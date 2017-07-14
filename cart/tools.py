from .models import CartItem
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect



def add_to_cart(request, product, qty ):
    product_in_cart = False
    try:
        cart_items = CartItem.my_query.current_session_and_active(cart_id=request.session['cart_id'])
        for cart_item in cart_items:
            if cart_item.product.id == product.id:
                check_qty = cart_item.qty + int(qty)
                if product.reserve >= check_qty:
                    cart_item.augment_quantity(quantity=qty)
                    product_in_cart=True
                    messages.success(request,'Προστέθηκε στο καλάθι %s ποσότητα στο προϊόν %s . '%(qty, product.title))
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    messages.warning(request,'Δεν υπάρχει υπόλοιπο την αποθήκη.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
        pass

    if not product_in_cart:
        ci = CartItem.objects.create(cart_id = request.session['cart_id'],
                                         qty = qty,
                                         product=product,
                                         )
        ci.save()



def summary_cost(request):
    pass