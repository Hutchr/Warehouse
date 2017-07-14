from rest_framework import serializers
from ..models import Comment
from django.contrib.contenttypes.models import ContentType

def create_comment_serializer(model_type='post', slug=None, parent_id=None):
    class CommentCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'parent', 'content', 'timestamp']

        def __init__(self, *args, **kwargs):
            self.model_type = model_type
            self.slug = slug
            self.parent_obj = None

            if self.parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    self.parent_obj = parent_qs.first()
            return super(CommentCreateSerializer, self).__init__(*args, **kwargs)
        def validate(self, data):
            model_type = self.model_type
            model_qs = ContentType.objects.filter(model=model_type)
            if not model_qs.exists():
                raise serializers.ValidationError("This is not valid")
            SomeModel = model_qs.first().model_class()
            obj_qs = SomeModel.objects.filter(slug=self.slug)
            if not obj_qs.exists() or obj_qs != 1:
                return serializers.ValidationError('this is not a slug for this project')




class CommentListSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['user', 'object_id', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.children:
            return obj.children().count()
        return 0

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count
        return 0

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    reply_count = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = '__all__'
    def get_reply_count(self, obj):
        return obj.children().count() if obj.parent else 0


class CommentChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'content_type', 'object_id', 'parent', 'content']


class CommentDetailSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'content_type', 'object_id', 'content', 'replies']

    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
        return None