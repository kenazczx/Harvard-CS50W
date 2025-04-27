from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/", views.search, name="search"),
    path("wiki/<str:title>", views.title, name="title"),
    path("create", views.create, name="create"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random_page", views.random_page, name="random_page")
]
