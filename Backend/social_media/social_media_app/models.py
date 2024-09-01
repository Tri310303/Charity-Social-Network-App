from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    avatar = CloudinaryField('avatar', null=True)


class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True, null=True)
    updated_date = models.DateField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class Hashtag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts_user')
    title = models.CharField(max_length=255, null=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='posts', null=True)
    hashtag = models.ManyToManyField(Hashtag)


class Interaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)

    class Meta:
        abstract = True


class Comment(Interaction):
    content = models.CharField(max_length=255, null=False)


class Like(Interaction):
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'post')


class Report(Interaction):
    REASON_CHOICES = [
        ('inappropriate_language', 'Ngôn ngữ không phù hợp'),
        ('spam', 'Spam'),
        ('no_payment_after_auction', 'Người dùng đấu giá nhưng không thanh toán'),
        ('other', 'Lý do khác')
    ]
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)

    def __str__(self):
        return f"Báo cáo về bài viết {self.post} bởi người dùng {self.user}"


class PostStatistics(BaseModel):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='statistics')
    comment_count = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='post_comments')
    like_count = models.ForeignKey(Like, on_delete=models.CASCADE, related_name='post_likes')


class Auction(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='auctions')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction_participants')
    bid_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions')


class Transaction(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_transactions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

#
# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE, related_name='notifications')
#
#     def __str__(self):
#         return self.content

