from rest_framework.generics import (
    ListAPIView, DestroyAPIView, RetrieveUpdateAPIView,
    UpdateAPIView, RetrieveAPIView, CreateAPIView,
    )
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination
from ..models import *
from ..api.serializers import *
from ..api.pagination import PostLimitOffsetPagination
from comment.api.serializers import CommentSerializer
from comment.models import Comment

class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated, OrderingFilter ]
    def perform_create(self, serializer):
        serializer.save(lead_content='gonna work!')

class PostListApiView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = [SearchFilter, ]
    search_fields = ['title']
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = Post.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(title__icontains=query)
        return queryset_list

class PostDetailAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

class PostUpdateAPIView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

