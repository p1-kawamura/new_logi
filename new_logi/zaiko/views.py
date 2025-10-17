from django.shortcuts import render,redirect
from .models import Shouhin,Place
import io
import csv
import json
from django.http import JsonResponse


def index(request):
    if "zaiko" not in request.session:
        request.session["zaiko"]={}
    if "place" not in request.session["zaiko"]:
        request.session["zaiko"]["place"]="物流センター"
    if "items" not in request.session["zaiko"]:
        request.session["zaiko"]["items"]=[]
    
    ses_item_list=request.session["zaiko"]["items"]
    order_list=order_item_list(ses_item_list)
    params={"order_list":order_list}

    return render(request,"zaiko/index.html",params)


#モーダル_品番検索に入力
def hinban_enter(request):
    hinban_enter=request.POST.get("hinban_enter")
    hinban_list=list(Shouhin.objects.filter(shouhin_set__icontains=hinban_enter).values_list("shouhin_set",flat=True).order_by("shouhin_set").distinct())
    d={"hinban_list":hinban_list}
    return JsonResponse(d)


#モーダル_品番リストをクリック
def hinban_click(request):
    hinban=request.POST.get("hinban")
    color_list=list(Shouhin.objects.filter(shouhin_set=hinban).values_list("color",flat=True).order_by("color").distinct())
    size_list=list(Shouhin.objects.filter(shouhin_set=hinban).values_list("size",flat=True).order_by("size_num").distinct())
    place_ok=list(Place.objects.filter(show=1))
    place_list=list(Shouhin.objects.filter(shouhin_set=hinban,place__in=place_ok).values_list("place",flat=True).distinct())
    place="物流センター"
    request.session["zaiko"]["place"]="物流センター"
    d={"color_list":color_list,
       "size_list":size_list,
       "item_list":item_list(hinban,[],[],place),
       "place_list":place_list,
       "place":place,
       }
    return JsonResponse(d)


#モーダル_カラー、サイズをクリック
def color_size_click(request):
    hinban=request.POST.get("hinban")
    color=request.POST.get("color")
    color=json.loads(color)
    size=request.POST.get("size")
    size=json.loads(size)
    place=request.session["zaiko"]["place"]
    d={"item_list":item_list(hinban,color,size,place)}
    return JsonResponse(d)


# FUNC　商品リスト取得
def item_list(hinban,color,size,place):
    if len(color)==0 and len(size)==0:
        item_list=list(Shouhin.objects.filter(shouhin_set=hinban,place=place).values().order_by("color","size_num"))
    else:
        if len(color)==0:
            item_list=list(Shouhin.objects.filter(shouhin_set=hinban,size__in=size,place=place).values().order_by("color","size_num"))
        elif len(size)==0:
            item_list=list(Shouhin.objects.filter(shouhin_set=hinban,color__in=color,place=place).values().order_by("color","size_num"))
        else:
            item_list=list(Shouhin.objects.filter(shouhin_set=hinban,color__in=color,size__in=size,place=place).values().order_by("color","size_num"))
    return item_list


# モーダル_拠点選択
def place_click(request):
    hinban=request.POST.get("hinban")
    color=request.POST.get("color")
    color=json.loads(color)
    size=request.POST.get("size")
    size=json.loads(size)
    place=request.POST.get("place")
    request.session["zaiko"]["place"]=place
    place_ok=list(Place.objects.filter(show=1))
    place_list=list(Shouhin.objects.filter(shouhin_set=hinban,place__in=place_ok).values_list("place",flat=True).distinct())
    d={
        "item_list":item_list(hinban,color,size,place),
        "place_list":place_list,
        "place":place,
        }
    return JsonResponse(d)


# モーダル_商品追加
def item_add(request):
    item_list=request.POST.get("item_list")
    item_list=json.loads(item_list)
    ses_item_list=request.session["zaiko"]["items"]
    for i in item_list:
        ses_item_list.append(i)
    request.session["zaiko"]["items"]=ses_item_list
    order_list=order_item_list(ses_item_list)

    d={"order_list":order_list}
    return JsonResponse(d)


# FUNC 依頼リスト
def order_item_list(ses_item_list):
    order_list=[]
    for i,h in enumerate(ses_item_list):
        hontai,kazu=map(int,h.split("_"))
        ins=Shouhin.objects.get(hontai_num=hontai)
        dic={
            "hinban":ins.shouhin_num,
            "hinmei":ins.shouhin_name,
            "color":ins.color,
            "size":ins.size,
            "kazu":kazu,
            "place":ins.place,
            "order_num":"order_" + str(i),
        }
        order_list.append(dic)
    return order_list


def item_del(request):
    order_num=request.POST.get("order_num")
    ses_item_list=request.session["zaiko"]["items"]
    del ses_item_list[int(order_num.replace("order_",""))]
    request.session["zaiko"]["items"]=ses_item_list
    order_list=order_item_list(ses_item_list)

    d={"order_list":order_list}
    return JsonResponse(d)












def csv_imp_page(request):
    return render(request,"zaiko/csv_imp.html")


def csv_imp(request):
    #在庫リスト
    data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)
        
    h=0
    for i in csv_list:
        if h!=0:
            Shouhin.objects.update_or_create(
                hontai_num=i[0],
                defaults={
                    "hontai_num":i[0],
                    "place":i[1],
                    "shouhin_num":i[2],
                    "shouhin_name":i[3],
                    "shouhin_set":i[4],
                    "color":i[5],
                    "size":i[6],
                    "size_num":i[7],
                    "available":i[8],
                    "keep":i[9],
                    "stock":i[10],
                    "tana":i[11],
                    "cost_price":i[12],
                    "bikou":i[13],
                    "attention":i[14],
                    "create_day":i[15],
                    "jan_code":i[16],
                    "sys_stock":i[17],
                    "sys_order":i[18],
                }            
            )
        h+=1

    return redirect("zaiko:csv_imp_page")


# 自由コード
def free(request):
    Shouhin.objects.all().delete()
    return redirect("zaiko:index")