from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path("login", views.login_view, name = "login"),
    path("logout", views.logout_view, name = "logout"),
    path("register", views.register, name = "register"),
    path("create", views.create, name = "create"),
    path("listing/<int:listing_id>", views.listing, name = "listing"),
    path("toggle_watchlist/<int:listing_id>", views.toggle_watchlist, name = "toggle_watchlist"),
    path("watchlist", views.watchlist, name = "watchlist"),
    path("close/<int:listing_id>", views.close, name = "close"),
    path("inactive", views.inactive, name = "inactive"),
    path("categories", views.categories, name = "categories"),
    path("listing/<str:category>", views.category_listing, name = "category_listing")
]
