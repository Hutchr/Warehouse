from django.shortcuts import render, render_to_response, get_list_or_404, get_object_or_404, HttpResponseRedirect,HttpResponse
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
from comment.models import Comment, CommentType
from .forms import *
from comment.forms import CommentForm
from mysite.models import WelcomePage
from products.models import CategorySite
from django.template.context_processors import csrf
from django.http import JsonResponse
from django.views import View
from django.contrib.contenttypes.models import ContentType
# Create your views here.


def blog_homepage(request):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    posts = Post.objects.all() or get_list_or_404
    post_category = PostCategory.objects.all()
    return render_to_response('obaju/blog.html',{'posts':posts,
                                                 'categories':categories,
                                                 'welcome_page':welcome_page,
                                                 'post_cat':post_category
                                                 })

def blog_category(request, slug):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    choosed_category = PostCategory.objects.get(slug=slug)
    posts = Post.objects.filter(category = choosed_category) or get_list_or_404
    post_category = PostCategory.objects.all()
    return render_to_response('obaju/blog.html',{'posts':posts,
                                                 'categories':categories,
                                                 'welcome_page':welcome_page,
                                                 'post_cat':post_category,
                                                 'choosed_category':choosed_category,
                                                 })

def blog_details(request,slug):
    welcome_page = WelcomePage.objects.get(id=1)
    categories = CategorySite.objects.all().filter(category__isnull=True).order_by('id')
    post_category = PostCategory.objects.all()
    post= Post.objects.get(slug=slug)
    content_type = post.get_content_type
    object_id = post.id
    comments = Comment.my_query.filter_by_instance(instance=post)

    if request.POST:
        form_comment = CommentForm(request.POST)
        if form_comment.is_valid():
            get_data = form_comment.cleaned_data.get('content')
            new_comment = Comment.objects.create(content_type=content_type,
                                                object_id =object_id,
                                                user=request.user,
                                                comment_type=CommentType.objects.get(id = 1),
                                                content = get_data,
                                                )
            new_comment.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form_comment = CommentForm()

    context = {
        'post': post,
        'blog_detail': True,
        'categories': categories,
        'welcome_page': welcome_page,
        'post_cat': post_category,
        'comments': comments,
        'form_comment': form_comment,

    }
    context.update(csrf(request))

    return render(request,'obaju/post.html',context)

def create_post(request):
    posts = Post.objects.all() or get_list_or_404
    if request.POST:
        form = PostCreate(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/blog/')
    else:
        form = PostCreate()
    context = {
        'posts': posts,
        'create': True,
        'form': form,
        }
    return render(request,'blog/blog_homepage.html',context)


def author_create_popup(request):
    form = AuthorForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))
    context = locals()
    return render(request, 'blog/category_post_popup.html', context)

def author_edit_popup(request, dk):
    instance = get_object_or_404(PostCategory, pk=dk)
    form = AuthorForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))
    context = locals()
    return render(request, 'blog/category_post_popup.html', context)

@csrf_exempt
def get_author_id(request):
    if request.is_ajax():
        author_name = request.GET['author_name']
        author_id = AuthorForm.objects.get(title=author_name).id
        data = {'author_id': author_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse('/')


def edit_post(request,slug):
    posts  = Post.objects.all() or get_list_or_404
    post= Post.objects.get(slug=slug)
    if request.POST:
        form = PostCreate(request.POST,instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/blog/')
    else:
        form = PostCreate(instance=post)
    context = {
        'posts':posts,
        'create':True,
        'form':form,
        }
    context.update(csrf(request))
    return render(request, 'blog/blog_homepage.html',context)

def on_fly_create_blog(request):
    title = 'Create Page'
    photos = BlogGallery.objects.all()
    if 'gallery' in request.POST:
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
    else:
        form = PhotoForm()
    if 'new_post' in request.POST:
        form_post = PostCreate(request.POST, request.FILES)
        if form_post.is_valid():
            form_post.save()
    context = locals()
    context.update(csrf(request))
    return render(request, 'blog/on_fly.html', context)

def create_gallery_image(request):
    images = BlogGallery.objects.all()
    if request.POST:
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url':photo.file.url}
        else:
            data = {'is_valid': False}
        return HttpResponse(data)
    else:
        form = GalleryForm()
    context = locals()
    context.update(csrf(request))
    return render(request, 'blog/create_gallery.html', context)