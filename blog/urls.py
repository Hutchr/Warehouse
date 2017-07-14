from django.conf.urls import url, include
from comment.api.views import *
from .views import *
from .api.views import *

urlpatterns = [
    url(r'^$', view=blog_homepage, name='blog_homepage'),
    url(r'^category/(?P<slug>[-\w]+)/$', view=blog_category, name='blog_category'),
    url(r'^create/$', view=create_post, name='blog_create'),

    url(r'^author/create/$', view=author_create_popup, name='AuthorCreate'),
    url(r'^author/(?P<pk>\d+)/edit', view=author_edit_popup, name='AuthorEdit'),
    url(r'^author/ajax/get_author_id', view=get_author_id, name="get_author_id"),

    url(r'^edit/(?P<slug>[-\w]+)/$', view=edit_post, name='blog_edit'),
    url(r'^edit/(?P<slug>[-\w]+)/$', view=edit_post, name='blog_edit'),
    url(r'^detail/(?P<slug>[-\w]+)/$', view=blog_details, name='blog_detail'),
    url(r'^create/on-fly/$', view=on_fly_create_blog, name='blog_create_fly'),
    url(r'^create/gallery-image/$', view=create_gallery_image, name='create_gallery_image'),
    url(r'^api/posts/$', PostListApiView.as_view(), name='api_posts'),
    url(r'^api/posts/create/$', PostCreateAPIView.as_view(), name='api_post_create'),
    url(r'^api/posts/detail/(?P<slug>[-\w]+)/$', PostDetailAPIView.as_view(), name='api_post_detail'),
    url(r'^api/posts/update/(?P<slug>[-\w]+)/$', PostUpdateAPIView.as_view(), name='api_post_update'),
    url(r'^api/posts/delete/(?P<slug>[-\w]+)/$', PostDeleteAPIView.as_view(), name='api_post_delete'),

    url(r'^api/comments/$', CommentListApiView.as_view(), name='api_comments'),
    url(r'^api/comments/create/$', CommentCreateAPIView.as_view(), name='api_comment_create'),
    url(r'^api/comments/(?P<pk>[-\w]+)/$', CommentDetailAPIView.as_view(), name='api_comment_detail'),
    #url(r'^api/posts/update/(?P<slug>[-\w]+)/$', PostUpdateAPIView.as_view(), name='api_post_update'),
    #url(r'^api/posts/delete/(?P<slug>[-\w]+)/$', PostDeleteAPIView.as_view(), name='api_post_delete'),

    ]

