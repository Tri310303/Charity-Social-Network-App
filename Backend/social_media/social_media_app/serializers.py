from .models import User
from rest_framework import serializers
from .models import Category, Post, Hashtag, Comment, PostStatistics, Report


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name']


class BaseSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='image')
    hashtag = HashtagSerializer(many=True)

    def get_image(self, avatar):
        if avatar.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % avatar.image.name)
            return '/static/%s' % avatar.image.name


class PostSerializer(BaseSerializer):
    hashtag = HashtagSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'hashtag']

    def create(self, validated_data):
        hashtag_data = validated_data.pop('hashtag')  # Lấy dữ liệu của trường hashtags
        post = Post.objects.create(**validated_data)  # Tạo đối tượng Post

        for hashtag_data in hashtag_data:
            hashtag, created = Hashtag.objects.get_or_create(**hashtag_data)
            post.hashtag.add(hashtag)  # Thêm hashtag vào bài viết

        return post


class PostDetailsSerializer(PostSerializer):
    liked = serializers.SerializerMethodField()

    def get_liked(self, post):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return post.like_set.filter(active=True).exists()

    class Meta:
        model = PostSerializer.Meta.model
        fields = list(PostSerializer.Meta.fields) + ['liked']


class PostStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostStatistics
        fields = ['post', 'comment_count', 'like_count']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password', 'is_superuser', 'is_staff', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()

        user = User(**data)
        user.set_password(data['password'])
        user.save()

        return user


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


# class InteractionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Interaction
#         fields = '__all__'
#
#
# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = '__all__'
