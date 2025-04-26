from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:auction_id>", views.listing, name="listing"),
    path("bid/<int:auction_id>", views.bid, name="bid"),
    path("close_auction/<int:auction_id>", views.close_auction, name="close_auction"),
    path("create_comment/<int:auction_id>", views.create_comment, name="create_comment"),
    path("manage_watchlist/<int:auction_id>", views.manage_watchlist, name="manage_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category")
]
