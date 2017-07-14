from rest_framework.generics import *
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination
from ..models import *
from ..api.serializers import *
from blog.api.pagination import PostLimitOffsetPagination

class CommentCreateAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated, OrderingFilter]

    def perform_create(self, serializer):
        serializer.save(lead_content='gonna work!')

class CommentListApiView(ListAPIView):
    queryset = Comment.my_query.is_parent()
    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = [SearchFilter, ]
    search_fields = ['title']
    #pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = Comment.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(title__icontains=query)
        return queryset_list

class CommentDetailAPIView(RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

class CommentUpdateAPIView(UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

class CommentDeleteAPIView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'





