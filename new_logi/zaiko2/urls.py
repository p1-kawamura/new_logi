from django.urls import path
from django.contrib.auth import views as auth_views
from .views import henshu_index,henshu_hinban_enter,henshu_hinban_click,henshu_color_size_click,henshu_list_click,henshu_up,henshu_del,henshu_excel_download, \
                    size_index,size_num_func,size_new,size_name,size_del,size_same,nyuuko_index,excel_download,excel_import,nyuuko_send, \
                    vba_irai_list,vba_hassou_data


app_name="zaiko2"
urlpatterns = [
    path('henshu_index', henshu_index, name="henshu_index"),
    path('henshu_hinban_enter', henshu_hinban_enter, name="henshu_hinban_enter"),
    path('henshu_hinban_click', henshu_hinban_click, name="henshu_hinban_click"),
    path('henshu_color_size_click', henshu_color_size_click, name="henshu_color_size_click"),
    path('henshu_list_click', henshu_list_click, name="henshu_list_click"),
    path('henshu_up', henshu_up, name="henshu_up"),
    path('henshu_del', henshu_del, name="henshu_del"),
    path('henshu_excel_download', henshu_excel_download, name="henshu_excel_download"),
    path('size_index', size_index, name="size_index"),
    path('size_num_func', size_num_func, name="size_num_func"),
    path('size_new', size_new, name="size_new"),
    path('size_name', size_name, name="size_name"),
    path('size_del', size_del, name="size_del"),
    path('size_same', size_same, name="size_same"),
    path('nyuuko_index', nyuuko_index, name="nyuuko_index"),
    path('excel_download', excel_download, name="excel_download"),
    path('excel_import', excel_import, name="excel_import"),
    path('nyuuko_send', nyuuko_send, name="nyuuko_send"),
    path('vba_irai_list', vba_irai_list, name="vba_irai_list"),
    path('vba_hassou_data', vba_hassou_data, name="vba_hassou_data"),
]