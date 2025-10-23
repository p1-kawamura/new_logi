from django.contrib import admin
from .models import Shouhin,Place,Shozoku,Size
from django.contrib.admin import ModelAdmin


class A_shouhin(ModelAdmin):
    model=Shouhin
    list_display=["hontai_num","place","shouhin_num","shouhin_name","color","size","stock"]
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


admin.site.register(Shouhin,A_shouhin)
admin.site.register(Place,A_place)
admin.site.register(Shozoku,A_shozoku)
admin.site.register(Size,A_size)