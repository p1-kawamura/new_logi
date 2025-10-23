from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index,hinban_enter,hinban_click,color_size_click,place_click,item_add,item_del,order_item_list,order_csv_check,csv_item_add, \
                    irai_send_check,irai_send_ok, \
                    csv_imp,csv_imp_page,free


app_name="zaiko"
urlpatterns = [
    path('', index, name="index"),
    path('hinban_enter/', hinban_enter, name="hinban_enter"),
    path('hinban_click/', hinban_click, name="hinban_click"),
    path('color_size_click/', color_size_click, name="color_size_click"),
    path('place_click/', place_click, name="place_click"),
    path('item_add/', item_add, name="item_add"),
    path('item_del/', item_del, name="item_del"),
    path('order_item_list/', order_item_list, name="order_item_list"),
    path('order_csv_check/', order_csv_check, name="order_csv_check"),
    path('csv_item_add/', csv_item_add, name="csv_item_add"),
    path('irai_send_check/', irai_send_check, name="irai_send_check"),
    path('irai_send_ok/', irai_send_ok, name="irai_send_ok"),

    path('csv_imp/', csv_imp, name="csv_imp"),
    path('csv_imp_page/', csv_imp_page, name="csv_imp_page"),
    path('free/', free, name="free"),
]