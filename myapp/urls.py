from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserOrderView, name="myorders"),
    path("login/", views.loginView, name="login"),
    path("register/", views.registerView, name="register"),
    path("wallet/", views.walletView, name="wallet"),
    path("logout/", views.logoutView, name="logout"),
    path("orders/", views.activeOrdersView, name="activeorders"),
    path("publish/", views.publishOrderView, name="publishorder"),
    
]