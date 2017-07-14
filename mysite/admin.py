from django.contrib import admin
from .models import *
# Register your models here.

class OfferInline(admin.TabularInline):
    model = OfferPage
    extra = 1

class BannerInline(admin.TabularInline):
    model = Banners
    extra = 3
    readonly_fields = ['image_tag_tiny']
    fields = ['status', 'image_tag_tiny', 'image', 'title', 'alt', 'href']

class MessagesInline(admin.TabularInline):
    model = FrontPageMessages
    extra = 3

class SecondsBannersInline(admin.TabularInline):
    model = SecondSectionBanners
    extra = 3

class FooterInline(admin.TabularInline):
    model = Footer
    extra = 1

class OfferAdmin(admin.ModelAdmin):
    list_filter = ['page_related', 'active']
    list_display = ['title', 'active', ]

class BannerAdmin(admin.ModelAdmin):
    readonly_fields = ['image_tag']
    list_display = ['image_tag_tiny', 'title' ,'status']
    list_filter = ['status', 'page_related']
    fields = [ 'image_tag', 'image', 'title', 'alt', 'href', 'status']

class SecondBannersAdmin(admin.ModelAdmin):
    readonly_fields = ['image_tag']
    list_display = ['image_tag_tiny', 'title' ,'active']
    list_filter = ['active']
    fields = ['active', 'image_tag', 'image', 'title', 'alt', 'href']

class WelcomePageAdmin(admin.ModelAdmin):
    readonly_fields = ['logo_tag', 'logo_small_tag']
    list_display = ['title', 'active']
    list_filter = ['active']
    inlines = [OfferInline, BannerInline, MessagesInline, SecondsBannersInline, FooterInline]
    fieldsets = (
        ('Βασικά Στοιχεία',{
            'fields':(('title', 'active'),
                      ('seo_keywords', 'seo_description'),
                      ('logo_tag', 'logo'),
                      ('logo_small_tag', 'logo_small'),),
        }),
        ('Πάνω Μενού',{
            'fields':(('login_text', 'info', 'phone_number',),),
        }),

    )

admin.site.register(WelcomePage, WelcomePageAdmin)
admin.site.register(Banners, BannerAdmin)
admin.site.register(FrontPageMessages)
admin.site.register(SecondSectionBanners, SecondBannersAdmin)
admin.site.register(Footer)
admin.site.register(FooterCategory)
admin.site.register(CompanyInfo)
admin.site.register(EshopInformation)
admin.site.register(EshopAskQuestions)
admin.site.register(SiteSettings)
admin.site.register(UserTerms)
admin.site.register(OfferPage, OfferAdmin)
