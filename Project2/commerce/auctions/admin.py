from django.contrib import admin
from .models import Auction, Bids, Comments, User
# Register your models here.
admin.site.register(Auction)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(User)