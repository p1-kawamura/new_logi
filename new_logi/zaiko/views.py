from django.shortcuts import render,redirect
from .models import Shouhin,Place,Shozoku,Size,Irai_list,Irai_detail
import io
import csv
import json
from django.http import JsonResponse
from datetime import datetime,timedelta,time
import os
from django.http import FileResponse
from django.conf import settings
import jpholiday
from django.db.models import Max


# 出荷作業依頼書_ダウンロード
def download_excel_1(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'excel', '★出荷作業依頼書（原紙）.xlsm')
    os.path.exists(file_path)
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename='★出荷作業依頼書（原紙）.xlsm')
    response['Content-Type'] = 'application/vnd.ms-excel.sheet.macroEnabled.12'
    return response


# 資材・カタログ出荷依頼_ダウンロード
def download_excel_2(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'excel', '資材・カタログ出荷依頼（社内・原紙）.xlsm')
    os.path.exists(file_path)
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename='資材・カタログ出荷依頼（社内・原紙）.xlsm')
    response['Content-Type'] = 'application/vnd.ms-excel.sheet.macroEnabled.12'
    return response


# 在庫依頼_index
def index(request):
    if "zaiko" not in request.session:
        request.session["zaiko"]={}
    if "place" not in request.session["zaiko"]:
        request.session["zaiko"]["place"]="物流センター"
    if "items" not in request.session["zaiko"]:
        request.session["zaiko"]["items"]=[]
    
    shozoku_list=Shozoku.objects.all()
    ses_item_list=request.session["zaiko"]["items"]
    order_list=order_item_list(ses_item_list)
    alert=0
    for i in order_list:
        if i["zaiko"]=="ng":
            alert += 1

    # 発送日
    # today=datetime(2025,11,5,9,0,0)
    today=datetime.today()
    regular_day,regular_att=get_regular_day(today)
    hurry_day=get_hurry_day(today)
    hurry_show=True
    if regular_day < hurry_day:
        hurry_show=False

    params={
        "shozoku_list":shozoku_list,
        "order_list":order_list,
        "alert":alert,
        "regular":get_day_show(regular_day),
        "regular_day":str(regular_day),
        "regular_att":regular_att,
        "hurry":get_day_show(hurry_day),
        "hurry_day":str(hurry_day),
        "hurry_show":hurry_show
    }
    return render(request,"zaiko/index.html",params)


# FUNC 通常便計算
def get_regular_day(today):
    if today.weekday() in [0,2,4] and jpholiday.is_holiday(today)==False and today.time()<time(10,0,0):
        regular_day=today
        regular_attention="yes"
    else:
        target_day=today + timedelta(days=1)
        while True:
            if target_day.weekday() in [0,2,4] and jpholiday.is_holiday(target_day)==False:
                regular_day=target_day
                regular_attention="no"
                break
            else:
                target_day += timedelta(days=1)
    return (regular_day.date(),regular_attention)


# FUNC お急ぎ便計算
def get_hurry_day(today):
    target_day=today + timedelta(days=1)
    while True:
        if target_day.weekday() not in [5,6] and jpholiday.is_holiday(target_day)==False:
            hurry_day=target_day
            break
        else:
            target_day += timedelta(days=1)
    return hurry_day.date()


# FUNC 日付（表示用）
def get_day_show(day):
    week=["月", "火", "水", "木", "金", "土", "日"]
    day=f"{day.month}月{day.day}日（{week[day.weekday()]}）"
    return day


# ajax_通常便計算
def ajax_regular_day(request):
    today=datetime.today()
    regular_day,regular_att=get_regular_day(today)
    d={"regular":get_day_show(regular_day),"regular_day":regular_day}
    return JsonResponse(d)


# モーダル_品番検索に入力
def hinban_enter(request):
    hinban_enter=request.POST.get("hinban_enter")
    hinban_list=list(Shouhin.objects.filter(shouhin_set__icontains=hinban_enter).values_list("shouhin_set",flat=True).order_by("shouhin_set").distinct())
    d={"hinban_list":hinban_list}
    return JsonResponse(d)


# モーダル_品番リストをクリック
def hinban_click(request):
    hinban=request.POST.get("hinban")
    color_list=list(Shouhin.objects.filter(shouhin_set=hinban).values_list("color",flat=True).order_by("color").distinct())
    size_list=list(Shouhin.objects.filter(shouhin_set=hinban).values_list("size",flat=True).order_by("size_num").distinct())
    place_ok=list(Place.objects.filter(show=1))
    place_list=list(Shouhin.objects.filter(shouhin_set=hinban,place__in=place_ok).values_list("place",flat=True).distinct())
    place="物流センター"
    request.session["zaiko"]["place"]="物流センター"
    ses_item_list=request.session["zaiko"]["items"]

    d={"color_list":color_list,
       "size_list":size_list,
       "item_list":item_list(hinban,[],[],place),
       "place_list":place_list,
       "place":place,
       "ses_list":ses_list(ses_item_list)
       }
    return JsonResponse(d)


# モーダル_カラー、サイズをクリック
def color_size_click(request):
    hinban=request.POST.get("hinban")
    color=request.POST.get("color")
    color=json.loads(color)
    size=request.POST.get("size")
    size=json.loads(size)
    place=request.session["zaiko"]["place"]
    ses_item_list=request.session["zaiko"]["items"]
    d={
        "item_list":item_list(hinban,color,size,place),
        "ses_list":ses_list(ses_item_list)
        }
    return JsonResponse(d)


# FUNC 商品リスト取得
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


# FUNC 追加済み商品取得
def ses_list(ses_item_list):
    ses_list=[]
    for i in ses_item_list:
        ses_list.append(i.split("_")[0])
    return ses_list


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
    ses_item_list=request.session["zaiko"]["items"]
    d={
        "item_list":item_list(hinban,color,size,place),
        "place_list":place_list,
        "place":place,
        "ses_list":ses_list(ses_item_list)
        }
    return JsonResponse(d)


# モーダル_商品追加
def item_add(request):
    item_lists=request.POST.get("item_list")
    item_lists=json.loads(item_lists)
    hinban=request.POST.get("hinban")
    color=request.POST.get("color")
    color=json.loads(color)
    size=request.POST.get("size")
    size=json.loads(size)
    ses_item_list=request.session["zaiko"]["items"]
    place=request.session["zaiko"]["place"]

    for i in item_lists:
        ses_item_list.append(i)
    request.session["zaiko"]["items"]=ses_item_list

    d={
        "order_list":order_item_list(ses_item_list),
        "ses_list":ses_list(ses_item_list),
        "item_list":item_list(hinban,color,size,place)
        }
    return JsonResponse(d)


# FUNC 依頼リスト
def order_item_list(ses_item_list):
    order_list=[]
    for i in ses_item_list:
        hontai,kazu=map(int,i.split("_"))
        ins=Shouhin.objects.get(hontai_num=hontai)
        if kazu > ins.available:
            zaiko="ng"
        else:
            zaiko="ok"
        dic={
            "hinban":ins.shouhin_num,
            "hinmei":ins.shouhin_name,
            "color":ins.color,
            "size":ins.size,
            "kazu":kazu,
            "hontai_kazu":"order_" + i,
            "place":ins.place,
            "zaiko":zaiko,
        }
        order_list.append(dic)
    return order_list


# モーダル_発注CSV_取込
def order_csv_check(request):
    text=request.POST.get("text")
    text=text.replace('"','')
    rows=text.split("\n")
    order_list=[]
    for i in range(1,len(rows)-1):
        row_list=rows[i].split(",")
        order_list.append({"hinmei":row_list[1],"jan_code":row_list[8],"kazu":row_list[6]})

    for i in order_list:
        ins=Shouhin.objects.filter(jan_code=i["jan_code"],sys_order=1)
        if ins.count()>1:
            i["result"]="JAN重複"
        elif ins.count()==0:
            i["result"]="連動"
        else:
            ses_item_list=request.session["zaiko"]["items"]
            ses_lists=ses_list(ses_item_list)
            if str(ins[0].hontai_num) in ses_lists:
                i["result"]="リスト"
            elif ins[0].available < int(i["kazu"]):
                i["result"]="在庫"
            else:
                i["result"]="OK"
                i["hontai_kazu"]="csv_" + str(ins[0].hontai_num) + "_" + str(i["kazu"])
    
    d={"order_csv":order_list}
    return JsonResponse(d)


# モーダル_発注CSV_商品追加
def csv_item_add(request):
    item_lists=request.POST.get("item_list")
    item_lists=json.loads(item_lists)
    ses_item_list=request.session["zaiko"]["items"]

    for i in item_lists:
        ses_item_list.append(i)
    request.session["zaiko"]["items"]=ses_item_list

    d={"order_list":order_item_list(ses_item_list)}
    return JsonResponse(d)


# 依頼商品一覧から削除
def item_del(request):
    hontai_kazu=request.POST.get("hontai_kazu").replace("order_","")
    ses_item_list=request.session["zaiko"]["items"]
    ses_item_list.remove(hontai_kazu)
    request.session["zaiko"]["items"]=ses_item_list
    order_list=order_item_list(ses_item_list)

    d={"order_list":order_list}
    return JsonResponse(d)


# 依頼送信_最終確認
def zaiko_last_check(request):
    ses_item_list=request.session["zaiko"]["items"]
    order_list=order_item_list(ses_item_list)
    alert=0
    for i in order_list:
        if i["zaiko"]=="ng":
            alert += 1

    d={"order_list":order_list,"alert":alert}
    return JsonResponse(d)


# 依頼確定（在庫出荷 / キープ / カタログ）
def irai_send_all(request):
    irai_dic=request.POST.get("irai_dic")
    dic=json.loads(irai_dic)
    irai_type=dic["irai_type"]
    try:
        irai_num=Irai_list.objects.all().aggregate(Max("irai_num"))["irai_num__max"] + 1
    except:
        irai_num=1

    ####### Irai_list #######
    if irai_type in ["zaiko","catalog"]:
        if dic["btn_t1"]=="regular":
            hassou_type=1
        else:
            hassou_type=2

    # 在庫出荷
    if irai_type=="zaiko":
        Irai_list.objects.create(
            irai_num=irai_num,
            shozoku=dic["shozoku"],
            tantou=dic["tantou"],
            irai_type=0,
            hassou_type=hassou_type,
            hassou_day=dic["btn_t1_day"],
            zaiko_type=dic["btn_t2"],
            zaiko_kakouba=dic["kakouba"],
            zaiko_gara=dic["gara"],
            zaiko_cus=dic["cus"],
            zaiko_system=dic["system"],
            bikou=dic["bikou"],
        )
    # キープ
    elif irai_type=="keep":
        Irai_list.objects.create(
            irai_num=irai_num,
            shozoku=dic["shozoku"],
            tantou=dic["tantou"],
            irai_type=1,
            irai_status=1,
            keep_cus=dic["keep_cus"],
        )
    # カタログ発送
    elif irai_type=="catalog":
        Irai_list.objects.create(
            irai_num=irai_num,
            shozoku=dic["shozoku"],
            tantou=dic["tantou"],
            irai_type=2,
            hassou_type=hassou_type,
            hassou_day=dic["btn_t1_day"],
            catalog_type=dic["btn_t2"],
            catalog_tempo=dic["tempo"],
            catalog_cus_com=dic["cus_dic"]["cat_com"],
            catalog_cus_name=dic["cus_dic"]["cat_name"],
            catalog_cus_yubin=dic["cus_dic"]["cat_yubin"],
            catalog_cus_pref=dic["cus_dic"]["cat_pref"],
            catalog_cus_city=dic["cus_dic"]["cat_city"],
            catalog_cus_banchi=dic["cus_dic"]["cat_banchi"],
            catalog_cus_build=dic["cus_dic"]["cat_build"],
            catalog_cus_tel=dic["cus_dic"]["cat_tel"],
            catalog_cus_mail=dic["cus_dic"]["cat_mail"],
            bikou=dic["bikou"],
        )

    ####### 商品 #######
    items=request.session["zaiko"]["items"]
    for i in items:
        hontai_num,kazu=map(int,i.split("_"))
        ins=Shouhin.objects.get(hontai_num=hontai_num)

        # Irai_detail
        Irai_detail.objects.create(
            irai_num=irai_num,
            hontai_num=ins.hontai_num,
            place=ins.place,
            shouhin_num=ins.shouhin_num,
            shouhin_name=ins.shouhin_name,
            color=ins.color,
            size=ins.size,
            size_num=ins.size_num,
            tana=ins.tana,
            cost_price=ins.cost_price,
            bikou=ins.bikou,
            attention=ins.attention,
            jan_code=ins.jan_code,
            kazu=kazu,
        )
        # Shouhin
        if irai_type in ["zaiko","catalog"]:
            ins.available -= kazu
        elif irai_type=="keep":
            ins.keep += kazu
            ins.available -= kazu
        ins.save()

    d={}
    return JsonResponse(d)


# 依頼履歴_一覧
def rireki_index(request):
    irai_list=Irai_list.objects.all()
    return render(request,"zaiko/rireki_list.html",{"irai_list":irai_list})


# 依頼履歴_詳細
def rireki_detail(request,irai_num):
    params={
        "irai":Irai_list.objects.filter(irai_num=irai_num).values()[0],
        "shouhin_list":Irai_detail.objects.filter(irai_num=irai_num).values(),
    }
    return render(request,"zaiko/rireki_index.html",params)











def csv_imp_page(request):
    return render(request,"zaiko/csv_imp.html")


def csv_imp(request):
    # #在庫リスト
    # data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    # csv_content = csv.reader(data)
    # csv_list=list(csv_content)
        
    # h=0
    # for i in csv_list:
    #     if h!=0:
    #         Shouhin.objects.update_or_create(
    #             hontai_num=i[0],
    #             defaults={
    #                 "hontai_num":i[0],
    #                 "place":i[1],
    #                 "shouhin_num":i[2],
    #                 "shouhin_name":i[3],
    #                 "shouhin_set":i[4],
    #                 "color":i[5],
    #                 "size":i[6],
    #                 "size_num":i[7],
    #                 "available":i[8],
    #                 "keep":i[9],
    #                 "stock":i[10],
    #                 "tana":i[11],
    #                 "cost_price":i[12],
    #                 "bikou":i[13],
    #                 "attention":i[14],
    #                 "create_day":i[15],
    #                 "jan_code":i[16],
    #                 "sys_stock":i[17],
    #                 "sys_order":i[18],
    #             }            
    #         )
    #     h+=1


    #サイズ表
    data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)
        
    h=0
    for i in csv_list:
        if h!=0:
            Size.objects.create(size_num=i[0],size=i[1])
        h+=1

    return redirect("zaiko:csv_imp_page")


# 自由コード
def free(request):
    Shouhin.objects.all().delete()
    return redirect("zaiko:index")