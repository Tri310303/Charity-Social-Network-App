from django.urls import path, include
from rest_framework import routers
from . import views

# Tạo một router mới
router = routers.DefaultRouter()

# Đăng ký các viewset với router
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'posts', views.PostDetailsViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'post-list', views.PostStatsViewSet, basename='post-stats')
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'categories', views.CategoryViewSet, basename='category')

# Thêm các đường dẫn đã đăng ký với router vào urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]

