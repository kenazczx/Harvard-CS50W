from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    
    
    def __str__(self):
        return f"{self.id}. Post was posted on {self.timestamp} by {self.user}"
    
    
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('follower', 'followed')
        
    def __str__(self):
        return f"{self.follower.username} followed {self.followed.username}"