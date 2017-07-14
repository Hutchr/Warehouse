from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import*

# Register your models here.

def site_active(modeladmin, request, queryset):
    for product in queryset:
        if product.status:
            product.status = False
        else:
            product.status = True
        product.save()
site_active.short_description = 'Eνεργοποίηση - Απενεργοποίηση Προϊόντος'

class ImageInline(admin.TabularInline):
    model = ProductPhotos
    extra = 3

class CharacteristicsInline(admin.TabularInline):
    model = ProductCharacteristics
    extra = 3

class SameColorProductsInline(admin.TabularInline):
    model = SameColorProducts
    extra = 1

class RelatedColorProductsInline(admin.TabularInline):
    model = RelatedProducts
    extra = 1

class BrandAdmin(admin.ModelAdmin):
    list_display = ['image_tag_tiny', 'title', 'is_active']
    list_filter = ['is_active']
    readonly_fields = ['image_tag']
    fields = ['image_tag', 'image', 'title', 'is_active', 'meta_keywords', 'meta_description', 'slug']

class CategorySiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status']
    list_filter = ['status', 'category']
    readonly_fields = ['image_tag', 'image_tag_tiny']
    fieldsets = (
        ('Γενικά Στοιχεία', {
            'fields': ('status',
                      ('image_tag', 'image'),
                      ('title', 'sort_order'),
                      ('content',),
                      'category',
                      )
        }),
        ('SEO',{
            'classes':('collapse',),
            'fields':(('slug', 'meta_description', 'meta_keywords'))
        }),
    )

class ProductCharacteristicAdmin(admin.ModelAdmin):
    list_filter = ['content_type']
    list_display = ['title', 'content_type', 'description']
    search_fields = ['title','content_type', 'description']
    fields = ['title', 'content_type', 'description']

class ProductAdmin(ImportExportModelAdmin):
    search_fields = ['title', 'brand__title', 'category_site__title', 'sku', 'color__title']
    readonly_fields = ['image_tag', 'image_back_tag']
    list_display = ['image_tag_tiny', 'title', 'status', 'color', 'sku', 'category_site', 'brand', 'price']
    list_filter = ['status', 'brand', 'category_site', 'color']
    inlines = [CharacteristicsInline, ImageInline,SameColorProductsInline, RelatedColorProductsInline]
    actions = [site_active, ]
    fieldsets = (
        ('Γενικά Στοιχεία', {
            'fields':('status', ('image_tag', 'image_back_tag',),
                      ('title', 'color',),
                      ('sku', 'internet_description', 'day_added'),
                      ('size', ),
                      ('brand', 'category_site', ),
                      )
        }),

        ('Αποθήκη',{
            'fields':('price', 'price_discount', 'qty', 'qty_kilo')
        }),
        ('SEO',{
            'classes':('collapse',),
            'fields':(('slug', 'meta_description', 'meta_keywords'))
        }),
    )

class SupplyAdmin(ImportExportModelAdmin):
    search_fields = ['title', 'phone', 'phone1', 'fax', 'email', 'site', 'afm' ]
    list_display = ['title', 'phone', 'phone1', 'fax', 'email', 'site', 'doy', 'afm',]
    list_filter = ['doy',]
    fieldsets = (
        ('Στοιχεία',{
            'fields':('title',('phone','phone1','fax'),('email','site'),'address','description')
        }),
        ('Οικονομικά Στοιχεία',{
            'classes':('collapse',),
            'fields':(('doy','afm'),'balance', 'remaining_deposit')
        }),

    )

class PhotoAdmin(admin.ModelAdmin):
    list_display = ['image_tag_tiny', 'title', 'active', 'is_primary', 'is_back']
    list_filter = ['product', 'active', 'is_primary', 'is_back']
    readonly_fields = ['image_tag']
    fields = ['active','image_tag', 'image', 'product', 'title', 'is_primary', 'is_back', 'alt']

class CategoryAdmin(ImportExportModelAdmin):
    pass



admin.site.register(Product, ProductAdmin)
admin.site.register(ProductPhotos, PhotoAdmin)
admin.site.register(ProductCharacteristics, ProductCharacteristicAdmin)
#admin.site.register(Category, CategoryAdmin)
#admin.site.register(Supply, SupplyAdmin)
#admin.site.register(Costumers)
#admin.site.register(TaxesCity)
admin.site.register(SameColorProducts)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(SizeAttribute)
admin.site.register(Brands, BrandAdmin)
admin.site.register(CategorySite, CategorySiteAdmin)
admin.site.register(Characteristics)
admin.site.register(CharacteristicsValue)
admin.site.register(RelatedProducts)



