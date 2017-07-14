from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from .models import *
from django.contrib import messages
import random

# Create your views here.

CART_ID_SESSION_KEY =''



def generate_cart_id():
    cart_id=''
    characters = 'ABCDEFGHIJKLMNOPQRQSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 50
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id



def card_id(request):
    try:
        is_there =  request.session['cart_id']
    except:
        request.session['cart_id'] = generate_cart_id()
    return request.session['cart_id']


def get_cart_items(request):
    cart_items = CartItem.current_session(card_id= card_id(request))
    return cart_items

def add_to_cart(request, dk):
    product = Product.objects.get(id=dk)
    qty = 1
    product_in_cart = False
    try:
        cart_items = CartItem.my_query.current_session_and_active(cart_id=request.session['cart_id'])
        for cart_item in cart_items:
            if cart_item.product.id == product.id:
                check_qty = cart_item.qty + 1
                if product.qty >= check_qty:
                    cart_item.augment_quantity(quantity=qty)
                    product_in_cart=True
                    messages.success(request,'Προστέθηκε στο καλάθι %s ποσότητα στο προϊόν %s . '%(qty, product.title))
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    messages.warning(request,'Δεν υπάρχει υπόλοιπο την αποθήκη.')
                    product_in_cart =True
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
        pass
    if not product_in_cart:
        if product.qty >= qty:
            ci = CartItem.objects.create(cart_id = request.session['cart_id'],
                                        qty = qty,
                                        product=product,
                                            )
            ci.save()
            messages.success(request,'Προστέθηκε το Προϊόν %s στο καλαθι.'%(product.title))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request,'Δεν υπάρχει υπόλοιπο την αποθήκη.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_to_cart_check_size(request, product):
    have_size = product.have_size()
    if not have_size:
        if 'add_item' in request.POST:
            qty = request.POST.get('qty')
            product_in_cart = False
            try:
                cart_items = CartItem.my_query.current_session_and_active(cart_id=request.session['cart_id'])
                for cart_item in cart_items:
                    if cart_item.product.id == product.id:
                        check_qty = cart_item.qty + int(qty)
                        if product.qty >= check_qty:
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
                messages.success(request,'Προστέθηκε στο καλάθι %s ποσότητα στο προϊόν %s . '%(qty, product.title))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        if 'add_item' in request.POST:
            qty = request.POST.get('qty') or 0
            size = request.POST.get('options')
            product_in_cart = False
            if size and int(qty) > 0:
                try:
                    cart_items = CartItem.my_query.current_session_and_active(cart_id=request.session['cart_id'])
                    for cart_item in cart_items:
                        if cart_item.product.id == product.id:
                            #if cart item have size i need to create another cart item to get the different number
                            if cart_item.size and cart_item.size != size:
                                ci = CartItem.objects.create(cart_id = request.session['cart_id'],
                                                 qty = qty,
                                                 product=product,
                                                 size=SizeAttribute.objects.get(id=size)
                                                 )
                                ci.save()
                                messages.success(request,'Προστέθηκε στο καλάθι %s ποσότητα στο προϊόν %s . '%(qty, product.title))
                                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                            check_qty = cart_item.qty + int(qty)
                            if product.qty >= check_qty:
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
                                                 size=SizeAttribute.objects.get(id=size)
                                                 )
                    ci.save()
                    messages.success(request,'Προστέθηκε στο καλάθι %s ποσότητα στο προϊόν %s . '%(qty, product.title))
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'Δεν συμπληρώσατε την φόρμα σωστά')


def remove_item_from_cart(request,dk):
    cart_item = get_object_or_404(CartItem,id=dk)
    cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cart_distinct_item_count(request):
    return get_cart_items(request).count()




