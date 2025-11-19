from django.contrib import admin
from .models import Shouhin,Place,Shozoku,Size,Irai_list,Irai_detail
from django.contrib.admin import ModelAdmin


class A_shouhin(ModelAdmin):
    model=Shouhin
    list_display=["hontai_num","place","shouhin_num","shouhin_name","color","size","available","stock"]
    search_fields=["shouhin_set"]
    ordering=["shouhin_num","color","size_num"]

class A_place(ModelAdmin):
    model=Place
    list_display=["place","show"]

class A_shozoku(ModelAdmin):
    model=Shozoku
    list_display=["id","shozoku"]

class A_size(ModelAdmin):
    model=Size
    list_display=["size_num","size"]

class A_irai_list(ModelAdmin):
    model=Irai_list
    list_display=["irai_num","irai_day","shozoku","tantou","irai_type","irai_status","hassou_type","hassou_day","place"]

class A_irai_detail(ModelAdmin):
    model=Irai_detail
    list_display=["irai_num","hontai_num","place","shouhin_num","shouhin_name","color","size","tana","kazu"]


admin.site.register(Shouhin,A_shouhin)
admin.site.register(Place,A_place)
admin.site.register(Shozoku,A_shozoku)
admin.site.register(Size,A_size)
admin.site.register(Irai_list,A_irai_list)
admin.site.register(Irai_detail,A_irai_detail)