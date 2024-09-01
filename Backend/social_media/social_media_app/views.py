from django.db.models import Sum, Count

from rest_framework import viewsets, generics, status, permissions, parsers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from . import serializers, paginators
from .models import Category, Post, User, Comment, Like, Auction, Hashtag, PostStatistics, Report, \
    Transaction
from . import perms
from rest_framework.permissions import AllowAny, IsAuthenticated


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class PostDetailsViewSet(viewsets.ViewSet):
    queryset = Post.objects.filter(active=True).all()
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticated]  # Sử dụng IsAuthenticated

    def create(self, request):
        serializer = serializers.PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk=None):
        if pk is None:
            pk = self.kwargs.get('pk')
        return get_object_or_404(self.queryset, pk=pk)

    def get_permissions(self):
        if self.action in ['update_post', 'delete_post', 'add_hashtag', 'add_comment', 'like']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    @action(methods=['patch'], detail=True)
    def update_post(self, request, pk=None):
        post = self.get_object(pk)
        serializer = serializers.PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def delete_post(self, request, pk=None):
        try:
            post = self.queryset.get(pk=pk)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], url_path='comments', detail=True)
    def add_comment(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        content = request.data.get('content')
        c = Comment.objects.create(user=request.user, post=post, content=content)

        return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='likes', detail=True)
    def like(self, request, pk):
        try:
            post = self.queryset.get(pk=pk)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                like.active = not like.active
                like.save()
            return Response(serializers.PostDetailsSerializer(post, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True)
    def add_hashtag(self, request, pk=None):
        post = self.get_object()  # Lấy bài viết dựa trên pk
        hashtag_names = request.data.get('hashtags', [])  # Lấy danh sách hashtag từ dữ liệu yêu cầu

        for hashtag_name in hashtag_names:
            # Kiểm tra xem hashtag đã tồn tại hay chưa, nếu chưa thì tạo mới
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
            # Thêm hashtag vào bài viết
            post.hashtags.add(hashtag)

        # Lưu lại thay đổi
        post.save()

        return Response({'message': 'Hashtags added to the post successfully'}, status=status.HTTP_200_OK)


class PostStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = paginators.PostPaginator
    queryset = Post.objects.filter(active=True)

    def list(self, request):
        queryset = self.queryset.order_by('-created_date')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = serializers.PostSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            # Thống kê theo thời gian
            stats_by_time = Post.objects.filter(active=True).values('created_date').annotate(
                post_count=Count('id'),
                likes_count=Sum('like__active'),  # Đếm số lượt like active
                comments_count=Sum('comment__active')  # Đếm số lượt comment active
            )
            # Thống kê theo danh mục
            stats_by_category = Post.objects.filter(active=True).values('category').annotate(
                post_count=Count('id'),
                likes_count=Sum('like__active'),  # Đếm số lượt like active
                comments_count=Sum('comment__active')  # Đếm số lượt comment active
            )

            return Response({
                'stats_by_time': stats_by_time,
                'stats_by_category': stats_by_category,
            })
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.OwnerAuthenticated]

    def list(self, request):
        try:
            post_id = request.query_params.get('post_id')  # Lấy post_id từ query parameters
            if not post_id:
                return Response({"message": "Parameter post_id is missing."}, status=status.HTTP_400_BAD_REQUEST)

            comments = Comment.objects.filter(post_id=post_id)
            if not comments:  # Kiểm tra nếu không có comment nào cho post_id này
                return Response({"message": "No comments found for the specified post."}, status=status.HTTP_200_OK)

            serializer = serializers.CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True).all()
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action.__eq__('current_user'):
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], url_path='current_user', url_name='current_user', detail=False)
    def current_user(self, request):
        return Response(serializers.UserSerializer(request.user).data)


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        try:
            user = request.user
            post_id = request.data.get('post_id')
            reason = request.data.get('reason')

            if not post_id or not reason:
                return Response({"message": "post_id and reason are required fields"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra xem post_id có tồn tại không
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return Response({"message": "Invalid post_id"}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra xem reason có hợp lệ không
            valid_reasons = [choice[0] for choice in Report.REASON_CHOICES]
            if reason not in valid_reasons:
                return Response({"message": "Invalid reason"}, status=status.HTTP_400_BAD_REQUEST)

            report_data = {
                'user': user.id,
                'post': post_id,
                'reason': reason
            }

            serializer = serializers.ReportSerializer(data=report_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class NotificationViewSet(viewsets.ModelViewSet):
#     queryset = Notification.objects.all()
#     serializer_class = serializers.NotificationSerializer
#
#
# class InteractionViewSet(viewsets.ModelViewSet):
#     queryset = serializers.InteractionSerializer.objects.all()
#     serializer_class = serializers.InteractionSerializer
