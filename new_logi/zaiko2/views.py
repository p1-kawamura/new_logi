from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from zaiko.models import Shouhin,Size,Place
import datetime
from django.http import JsonResponse
import io
import csv
import json


# 編集画面
def henshu_index(request):
    place_list=Place.objects.all()
    size_list=Size.objects.all()
    params={
        "size_list":size_list,
        "place_list":place_list,
    }
    return render(request,"zaiko2/henshu.html",params)


# 品番検索に入力
def henshu_hinban_enter(request):
    team=request.POST.get("team")
    hinban_enter=request.POST.get("hinban_enter")
    if team=="全店舗":
        hinban_list=list(Shouhin.objects.filter(shouhin_num__icontains=hinban_enter).values_list("shouhin_num",flat=True).order_by("shouhin_num").distinct())
    else:
        hinban_list=list(Shouhin.objects.filter(team=team,shouhin_num__icontains=hinban_enter).values_list("shouhin_num",flat=True).order_by("shouhin_num").distinct())
    d={"hinban_list":hinban_list}
    return JsonResponse(d)


# 編集_品番クリック
def henshu_hinban_click(request):
    team=request.POST.get("team")
    hinban=request.POST.get("hinban")
    item_list=list(Shouhin.objects.filter(team=team,shouhin_num=hinban).order_by("color","size_num").values())
    d={"item_list":item_list}
    return JsonResponse(d)


# 編集_リストクリック
def henshu_list_click(request):
    hontai_num=request.POST.get("hontai_num")
    item=list(Shouhin.objects.filter(hontai_num=hontai_num).values())[0]
    d={"item":item}
    return JsonResponse(d)


# 編集_登録/更新
def henshu_up(request):
    hontai_num=request.POST.get("hontai_num")
    team=request.POST.get("team")
    shouhin_num=request.POST.get("shouhin_num")
    shouhin_name=request.POST.get("shouhin_name")
    color=request.POST.get("color")
    size=request.POST.get("size")
    size_num=Size.objects.get(size=size).size_num
    tana=request.POST.get("tana")
    joutai=request.POST.get("joutai")
    rental_day=request.POST.get("rental_day")
    rental_tantou=request.POST.get("rental_tantou")
    rental_cus=request.POST.get("rental_cus")
    bikou=request.POST.get("bikou")

    # 新規登録
    if hontai_num=="":
        Shouhin.objects.create(
            team=team,shouhin_num=shouhin_num,shouhin_name=shouhin_name,color=color,size=size,size_num=size_num,
            tana=tana,joutai=joutai,rental_day=rental_day,rental_tantou=rental_tantou,rental_cus=rental_cus,bikou=bikou,
        )
    # 内容更新
    else:
        ins=Shouhin.objects.get(hontai_num=hontai_num)
        ins.team=team
        ins.shouhin_num=shouhin_num
        ins.shouhin_name=shouhin_name
        ins.color=color
        ins.size=size
        ins.size_num=size_num
        ins.tana=tana
        ins.joutai=joutai
        ins.rental_day=rental_day
        ins.rental_tantou=rental_tantou
        ins.rental_cus=rental_cus
        ins.bikou=bikou
        ins.save()

    d={}
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


# 新規サイズ追加
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

