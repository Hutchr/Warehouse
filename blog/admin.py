from django.contrib import admin
from .models import Post, PostCategory
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    pass

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'lead_content', 'publish']

admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)