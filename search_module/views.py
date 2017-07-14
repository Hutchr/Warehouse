from django.shortcuts import render
from .models import SearchTerm
from products.models import Product
from django.db.models import Q
# Create your views here.


STRIP_WORDS =['a','an','and','by','for','from','in','no','not',
'of','on','or','that','the','to','with']

def prepare_words(search_text):
    words = search_text.split()
    for common in STRIP_WORDS:
        if common in words:
            words.remove(common)
            return words[0:5]

def store(request,q):
    if len(q)>2:
        term = SearchTerm()
        term.q = q
        term.ip_address = request.META.get('REMOTE_ADDR')
        term.user = None
        if request.user.is_authenticated():
            term.user = request.user
        term.save()

def products(search_text):
    words = prepare_words(search_text)
    products = Product.my_query.active_with_qty()
    results = {}
    for word in words:
        products = products.filter(Q(title__icontains=word)|
                                   Q(description__icontains=word)|
                                   Q(brand__title__icontains=word)|
                                   Q(category_site__icontains=word)|
                                   Q(meta_description__icontains=word) |
                                   Q(meta_keywords__icontains=word)
                                   ).distinct()
        results['products'] = products
    return results
