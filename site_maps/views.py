from products.models import Product
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
import datetime



class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.day_added