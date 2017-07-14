from django.db import models
from django.conf import settings
from comment.models import Comment
from django.contrib.contenttypes.models import ContentType

# Create your models here.

MEDIAURL = 'media'

def project_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'blog/%s/%s' % (instance.title, filename)

def gallery_upload(instance, filename):
    return 'blog/gallery/%s/%s' % ('gallery', filename)

def post_upload():
    return '/post_images'

class PostTags(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class PostCategory(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    content = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name='Ονομασία Άθρου')
    image = models.FileField(upload_to=project_directory_path, verbose_name='Εικόνα', blank=True)
    lead_content = models.TextField(null=True, blank=True)
    content = models.TextField(verbose_name='Κείμενο')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    publish = models.DateField(auto_now=True, auto_now_add=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    slug = models.SlugField(unique=True,null=True, blank=True, allow_unicode=True)
    seo = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(PostCategory, null=True)
    author = models.ForeignKey(Author, null=True)
    def __str__(self):
        return self.title
        
    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


class BlogGallery(models.Model):
    file = models.ImageField(upload_to=gallery_upload)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'my_photo'
        verbose_name_plural = 'GalleryBlog'