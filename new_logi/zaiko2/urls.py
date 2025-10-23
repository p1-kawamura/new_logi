from django.urls import path
from django.contrib.auth import views as auth_views
from .views import henshu_index


app_name="zaiko2"
urlpatterns = [
    path('henshu_index', henshu_index, name="henshu_index"),
]