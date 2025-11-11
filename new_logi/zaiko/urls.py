from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index,hinban_enter,hinban_click,color_size_click,place_click,item_add,item_del,order_item_list,order_csv_check,csv_item_add, \
                    zaiko_last_check,ajax_regular_day,irai_send_all,rireki_index,rireki_detail,download_excel_1,download_excel_2, \
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
    path('zaiko_last_check/', zaiko_last_check, name="zaiko_last_check"),
    path('ajax_regular_day/', ajax_regular_day, name="ajax_regular_day"),
    path('irai_send_all/', irai_send_all, name="irai_send_all"),
    path('rireki_index/', rireki_index, name="rireki_index"),
    path('rireki_detail/<int:irai_num>', rireki_detail, name="rireki_detail"),

    path('download_excel_1/', download_excel_1, name="download_excel_1"),
    path('download_excel_2/', download_excel_2, name="download_excel_2"),
    path('csv_imp/', csv_imp, name="csv_imp"),
    path('csv_imp_page/', csv_imp_page, name="csv_imp_page"),
    path('free/', free, name="free"),
]