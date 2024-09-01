from django.contrib import admin
from .models import Category, Post, User, Comment, Like, PostStatistics, Report, Hashtag, Auction
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_date', 'updated_date', 'active')
    list_filter = ('category', 'created_date', 'updated_date', 'active')
    search_fields = ('title', 'user__username')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'post', 'created_date', 'active')
    list_filter = ('created_date', 'active')
    search_fields = ('content', 'user__username', 'post__title')


class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reason', 'created_date', 'active')
    list_filter = ('reason', 'created_date', 'active')
    search_fields = ('user__username', 'post__title')


class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'active')
    list_filter = ('active',)
    search_fields = ('user__username', 'post__title')


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'avatar', 'is_staff')
    list_filter = ('is_staff',)
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name','last_name', 'email', 'avatar')}),
        ('Permissions', {'fields': ('is_staff', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'email', 'password1', 'password2', 'avatar', 'is_staff')}
         ),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(PostStatistics)
admin.site.register(Report, ReportAdmin)
admin.site.register(Hashtag)
admin.site.register(Auction)
