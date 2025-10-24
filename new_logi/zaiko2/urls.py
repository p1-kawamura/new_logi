from django.urls import path
from django.contrib.auth import views as auth_views
from .views import henshu_index,henshu_hinban_enter,henshu_hinban_click,henshu_list_click,henshu_up,henshu_del, \
                    size_index,size_num,size_new,size_name,size_del,size_same


app_name="zaiko2"
urlpatterns = [
    path('henshu_index', henshu_index, name="henshu_index"),
    path('henshu_hinban_enter', henshu_hinban_enter, name="henshu_hinban_enter"),
    path('henshu_hinban_click', henshu_hinban_click, name="henshu_hinban_click"),
    path('henshu_list_click', henshu_list_click, name="henshu_list_click"),
    path('henshu_up', henshu_up, name="henshu_up"),
    path('henshu_del', henshu_del, name="henshu_del"),
    path('size_index', size_index, name="size_index"),
    path('size_num', size_num, name="size_num"),
    path('size_new', size_new, name="size_new"),
    path('size_name', size_name, name="size_name"),
    path('size_del', size_del, name="size_del"),
    path('size_same', size_same, name="size_same"),
]