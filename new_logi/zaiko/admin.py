from django.contrib import admin
from .models import Shouhin,Place
from django.contrib.admin import ModelAdmin


class A_shouhin(ModelAdmin):
    model=Shouhin
    list_display=["hontai_num","place","shouhin_num","shouhin_name","color","size","stock"]

class A_place(ModelAdmin):
    model=Place
    list_display=["place","show"]


admin.site.register(Shouhin,A_shouhin)
admin.site.register(Place,A_place)