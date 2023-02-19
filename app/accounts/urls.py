from django.urls import path
from . import views

urlpatterns = [
    path('isloggedin', views.is_logged, name="is_logged"),
    path('logout', views.logout_user, name="logout"),
    path('login', views.login_user, name="login"),
    path('register', views.register, name="register"),
    path('get_payment_profile', views.get_payment_profile, name="get_payment_profile")
]