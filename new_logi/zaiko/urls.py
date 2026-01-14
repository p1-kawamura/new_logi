from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index,check_0,hinban_enter,hinban_click,color_size_click,place_click,item_add,item_del,order_item_list,order_csv_check,csv_item_add, \
                    zaiko_last_check,ajax_regular_day,irai_send_all,rireki_index,rireki_search,rireki_detail,irai_change_today,irai_cancel, \
                    page_first,page_prev,page_next,page_last,download_excel_1, \
                    irai_reset,irai_keep_hassou,csv_imp,csv_imp_page,free


app_name="zaiko"
urlpatterns = [
    path('', index, name="index"),
    path('login/', auth_views.LoginView.as_view(template_name='zaiko/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('check_0/', check_0, name="check_0"),
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
    path('rireki_search/', rireki_search, name="rireki_search"),
    path('rireki_detail/<int:pk>', rireki_detail, name="rireki_detail"),
    path('irai_change_today/', irai_change_today, name="irai_change_today"),
    path('irai_cancel/', irai_cancel, name="irai_cancel"),
    path('irai_reset/', irai_reset, name="irai_reset"),
    path('irai_keep_hassou/', irai_keep_hassou, name="irai_keep_hassou"),
    path('page_first/', page_first, name="page_first"),
    path('page_prev/', page_prev, name="page_prev"),
    path('page_next/', page_next, name="page_next"),
    path('page_last/', page_last, name="page_last"),

    path('download_excel_1/', download_excel_1, name="download_excel_1"),
    path('csv_imp/', csv_imp, name="csv_imp"),
    path('csv_imp_page/', csv_imp_page, name="csv_imp_page"),
    path('free/', free, name="free"),
]