from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Auction", blank=True, related_name="watched_by")


class Auction(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(default="No description provided.")
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_auctions")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions_won", blank=True, null=True)

    def __str__(self):
        return f"Auction {self.id}: {self.title} starting bid at {self.starting_bid}"
    

class Bids(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey("Auction", on_delete=models.CASCADE, related_name="bids")
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} made a bid amount of ${self.amount} for an Auction for {self.listing.title}"

class Comments(models.Model):
    comment = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey("Auction", on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} commented {self.comment} on {self.listing} at {self.timestamp}"








# Need to add details about auction listings, bids, comments, and auction categories
# Everytime make a change, need to run python make migration and migrate for models
