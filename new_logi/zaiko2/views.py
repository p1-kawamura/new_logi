from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from zaiko.models import Shouhin,Size,Place
import datetime
from django.http import JsonResponse
import io
import csv
import json
from django.db.models import Max


# 編集画面
def henshu_index(request):
    place_list=Place.objects.all()
    size_list=Size.objects.all()
    params={
        "size_list":size_list,
        "place_list":place_list,
    }
    return render(request,"zaiko2/henshu.html",params)


# 編集_品番検索に入力
def henshu_hinban_enter(request):
    hinban=request.POST.get("hinban_enter")
    hinban_list=list(Shouhin.objects.filter(shouhin_set__icontains=hinban).values_list("shouhin_set",flat=True).order_by("shouhin_set").distinct())
    d={"hinban_list":hinban_list}
    return JsonResponse(d)


# 編集_品番クリック
def henshu_hinban_click(request):
    hinban=request.POST.get("hinban")
    item_list=list(Shouhin.objects.filter(shouhin_set=hinban).order_by("color","size_num").values())
    d={"item_list":item_list}
    return JsonResponse(d)


# 編集_リストクリック
def henshu_list_click(request):
    hontai_num=request.POST.get("hontai_num")
    item=Shouhin.objects.filter(hontai_num=hontai_num).values()[0]    
    d={"item":item}
    return JsonResponse(d)


# 編集_登録/更新
def henshu_up(request):
    dic=request.POST.get("dic")
    dic=json.loads(dic)
    dic["shouhin_set"]=dic["shouhin_num"] + "　" + dic["shouhin_name"]
    dic["size"]=Size.objects.get(size_num=dic["size_num"]).size
    kubun=0
    if dic["hontai_num"]=="":
        dic["hontai_num"]=Shouhin.objects.all().aggregate(Max("hontai_num"))["hontai_num__max"] + 1
        kubun=1

    Shouhin.objects.update_or_create(hontai_num=dic["hontai_num"],defaults=dic)
    d={"kubun":kubun}
    return JsonResponse(d)


# 編集_削除
def henshu_del(request):
    hontai_num=request.POST.get("hontai_num")
    Shouhin.objects.get(hontai_num=hontai_num).delete()
    d={}
    return JsonResponse(d)


# サイズ画面
def size_index(request):
    sizes=Size.objects.all().order_by("size_num")
    return render(request,"zaiko2/size.html",{"sizes":sizes})


# サイズ番号（順番）
def size_num(request):
    size_list=request.POST.get("size_list")
    size_list=json.loads(size_list)
    li=[]
    for key,value in size_list.items():
        li.append(value)
    # サイズ一覧
    for size in li:
        ins=Size.objects.get(size=size)
        if ins.size_num != li.index(size)+1:
            ins.size_num=li.index(size)+1
            ins.save()
    #商品一覧
    for size in li:
        ins=Shouhin.objects.filter(size=size)
        if ins.count() != 0:
            ins2=ins[0]
            if ins2.size_num != li.index(size)+1:
                for ins2 in ins:
                    ins2.size_num=li.index(size)+1
                    ins2.save()
    d={"":""}
    return JsonResponse(d)


# サイズ追加
def size_new(request):
    size_new=request.POST.get("size_new")
    Size.objects.create(size_num=0, size=size_new)
    d={"":""}
    return JsonResponse(d)


# サイズ名称
def size_name(request):
    old_n=request.POST.get("size_name1")
    new_n=request.POST.get("size_name2")
    # サイズ一覧
    ins=Size.objects.get(size=old_n)
    ins.size=new_n
    ins.save()
    #商品一覧
    ins=Shouhin.objects.filter(size=old_n)
    if ins.count() != 0:
        for ins2 in ins:
            ins2.size=new_n
            ins2.save()
    d={"":""}
    return JsonResponse(d)


# サイズ削除
def size_del(request):
    size_name=request.POST.get("size_name")
    Size.objects.get(size=size_name).delete()
    # サイズ一覧
    ins=Size.objects.all()
    for i,h in enumerate(ins):
        h.size_num=i+1
        h.save()
    #商品一覧
    ins=Shouhin.objects.all()
    for i in ins:
        i.size_num=Size.objects.get(size=i.size).size_num
        i.save()
    d={"":""}
    return JsonResponse(d)


# 同サイズ使用商品
def size_same(request):
    size_name=request.POST.get("size_name")
    size_same_list=list(Shouhin.objects.filter(size=size_name).values())
    d={"size_same_list":size_same_list}
    return JsonResponse(d)

