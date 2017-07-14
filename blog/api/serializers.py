from rest_framework import serializers
from ..models import Post
from comment.api.serializers import *




post_detail_url = serializers.HyperlinkedIdentityField(
        view_name='api_post_detail',
        lookup_field='slug',
    )

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'user', 'publish', 'slug']

class PostDetailSerializer(serializers.ModelSerializer):
    url = post_detail_url
    user = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = '__all__'

    def get_comments(self, obj):
        content_type = obj.get_content_type
        object_id = obj.id
        c_qs = Comment.objects.filter_by_instance(obj)
        comments = CommentSerializer(c_qs, many=True).data
        return comments
        
    def get_user(self, obj):
        return str(obj.user.username)
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostListSerializer(serializers.ModelSerializer):
    url = post_detail_url
    user = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['url', 'title', 'user', 'publish', 'slug']

    def get_user(self, obj):
        return str(obj.user.username)

    def get_image(self, obj):
        try:
            image = obj.image.url
        except:
            image = None
        return image
