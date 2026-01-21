from django.shortcuts import render,redirect
from .models import Shouhin,Place,Shozoku,Size,Irai_list,Irai_detail
from django.contrib.auth.decorators import login_required
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
from django.utils import timezone


# 出荷作業依頼書_ダウンロード
def download_excel_1(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'excel', '★出荷作業依頼書（原紙）.xlsx')
    os.path.exists(file_path)
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename='★出荷作業依頼書（原紙）.xlsx')
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response


# 在庫依頼_index
@login_required
def index(request):
    if "zaiko" not in request.session:
        request.session["zaiko"]={}
    if "place" not in request.session["zaiko"]:
        request.session["zaiko"]["place"]="物流センター"
    if "items" not in request.session["zaiko"]:
        request.session["zaiko"]["items"]=[]
    if "check_0" not in request.session["zaiko"]:
        request.session["zaiko"]["check_0"]="0"
    if "page_num" not in request.session["zaiko"]:
        request.session["zaiko"]["page_num"]=1
    if "all_page_num" not in request.session["zaiko"]:
        request.session["zaiko"]["all_page_num"]=""
    if "place2" not in request.session["zaiko"]:
        request.session["zaiko"]["place2"]="物流センター"
    if "items2" not in request.session["zaiko"]:
        request.session["zaiko"]["items2"]=[]
    if "rireki_search" not in request.session["zaiko"]:
        request.session["zaiko"]["rireki_search"]={}
    if "now_page" not in request.session["zaiko"]:
        request.session["zaiko"]["now_page"]="在庫"
    

    # キープ解除
    ins=Irai_list.objects.filter(irai_status=1)
    for i in ins:
        if timezone.now() - i.irai_day >= timedelta(days=21):
            i.irai_status=4
            i.cancel_day=datetime.now().strftime("%Y年%m月%d日 %H:%M")
            i.save()
            ins_det=Irai_detail.objects.filter(irai_num=i.irai_num,place=i.place)
            for h in ins_det:
                ins_sho=Shouhin.objects.get(hontai_num=h.hontai_num)
                ins_sho.keep -= h.kazu
                ins_sho.available += h.kazu
                ins_sho.save()

    # 依頼商品一覧
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

    request.session["zaiko"]["now_page"]="在庫"
    params={
        "shozoku_list":shozoku_list,
        "order_list":order_list,
        "alert":alert,
        "regular":get_day_show(regular_day),
        "regular_day":str(regular_day),
        "regular_att":regular_att,
        "hurry":get_day_show(hurry_day),
        "hurry_day":str(hurry_day),
        "hurry_show":hurry_show,
        "check_0":request.session["zaiko"]["check_0"],
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


# モーダル_発注可能数
def check_0(request):
    check_0=request.POST.get("check_0")
    request.session["zaiko"]["check_0"]=check_0
    d={}
    return JsonResponse(d)


# モーダル_品番検索に入力
def hinban_enter(request):
    hinban_enter=request.POST.get("hinban_enter")
    modal_type=request.POST.get("modal_type")
    check_0_ses=request.session["zaiko"]["check_0"]
    if modal_type=="zaiko" and check_0_ses=="1":
        hinban_list=list(Shouhin.objects.filter(shouhin_set__icontains=hinban_enter,available__gt=0).values_list("shouhin_set",flat=True).order_by("shouhin_set").distinct())
    else:
        hinban_list=list(Shouhin.objects.filter(shouhin_set__icontains=hinban_enter).values_list("shouhin_set",flat=True).order_by("shouhin_set").distinct())                         
    d={"hinban_list":hinban_list}
    return JsonResponse(d)


# モーダル_品番リストをクリック
def hinban_click(request):
    hinban=request.POST.get("hinban")
    modal_type=request.POST.get("modal_type")
    check_0_ses=request.session["zaiko"]["check_0"]
    place_ok=list(Place.objects.filter(show=1))

    if modal_type=="zaiko" and check_0_ses=="1":
        color_list=list(Shouhin.objects.filter(shouhin_set=hinban,available__gt=0).values_list("color",flat=True).order_by("color").distinct())
        size_list=list(Shouhin.objects.filter(shouhin_set=hinban,available__gt=0).values_list("size",flat=True).order_by("size_num").distinct())
        place_list=list(Shouhin.objects.filter(shouhin_set=hinban,place__in=place_ok,available__gt=0).values_list("place",flat=True).distinct())
    else:
        color_list=list(Shouhin.objects.filter(shouhin_set=hinban).values_list("color",flat=True).order_by("color").distinct())
        size_list=list(Shouhin.objects.filter(shouhin_set=hinban).values_list("size",flat=True).order_by("size_num").distinct())
        place_list=list(Shouhin.objects.filter(shouhin_set=hinban,place__in=place_ok).values_list("place",flat=True).distinct())

    place_dic={}
    for i in place_list:
        place_dic[i]=Place.objects.get(place=i).id
    place_list=sorted(place_dic, key=place_dic.get)

    place="物流センター"
    request.session["zaiko"]["place"]="物流センター"
    request.session["zaiko"]["place2"]="物流センター"
    ses_item_list=request.session["zaiko"]["items"]

    d={"color_list":color_list,
       "size_list":size_list,
       "item_list":item_list(hinban,[],[],place,modal_type,check_0_ses),
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
    modal_type=request.POST.get("modal_type")
    check_0_ses=request.session["zaiko"]["check_0"]
    if modal_type=="zaiko":
        place=request.session["zaiko"]["place"]
        ses_item_list=request.session["zaiko"]["items"]
    else:
        place=request.session["zaiko"]["place2"]
        ses_item_list=request.session["zaiko"]["items2"]
    d={
        "item_list":item_list(hinban,color,size,place,modal_type,check_0_ses),
        "ses_list":ses_list(ses_item_list)
        }
    return JsonResponse(d)


# FUNC 商品リスト取得
def item_list(hinban,color,size,place,modal_type,check_0_ses):
    if modal_type=="zaiko" and check_0_ses=="1":
        if len(color)==0 and len(size)==0:
            item_list=list(Shouhin.objects.filter(shouhin_set=hinban,place=place,available__gt=0).values().order_by("color","size_num"))
        else:
            if len(color)==0:
                item_list=list(Shouhin.objects.filter(shouhin_set=hinban,size__in=size,place=place,available__gt=0).values().order_by("color","size_num"))
            elif len(size)==0:
                item_list=list(Shouhin.objects.filter(shouhin_set=hinban,color__in=color,place=place,available__gt=0).values().order_by("color","size_num"))
            else:
                item_list=list(Shouhin.objects.filter(shouhin_set=hinban,color__in=color,size__in=size,place=place,available__gt=0).values().order_by("color","size_num"))
    else:
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
    modal_type=request.POST.get("modal_type")
    check_0_ses=request.session["zaiko"]["check_0"]

    place_ok=list(Place.objects.filter(show=1))
    place_list=list(Shouhin.objects.filter(shouhin_set=hinban,place__in=place_ok).values_list("place",flat=True).distinct())

    if modal_type=="zaiko":
        request.session["zaiko"]["place"]=place
        ses_item_list=request.session["zaiko"]["items"]
        if check_0_ses=="1":
            place_list=list(Shouhin.objects.filter(shouhin_set=hinban,place__in=place_ok,available__gt=0).values_list("place",flat=True).distinct())
    else:
        request.session["zaiko"]["place2"]=place
        ses_item_list=request.session["zaiko"]["items2"]
    
    place_dic={}
    for i in place_list:
        place_dic[i]=Place.objects.get(place=i).id
    place_list=sorted(place_dic, key=place_dic.get)
    
    d={
        "item_list":item_list(hinban,color,size,place,modal_type,check_0_ses),
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
    modal_type=request.POST.get("modal_type")
    check_0_ses=request.session["zaiko"]["check_0"]

    if modal_type == "zaiko":
        ses_item_list=request.session["zaiko"]["items"]
        place=request.session["zaiko"]["place"]
    else:
        ses_item_list=request.session["zaiko"]["items2"]
        place=request.session["zaiko"]["place2"]

    for i in item_lists:
        ses_item_list.append(i)

    if modal_type == "zaiko":
        request.session["zaiko"]["items"]=ses_item_list
    else:
        request.session["zaiko"]["items2"]=ses_item_list

    d={
        "order_list":order_item_list(ses_item_list),
        "ses_list":ses_list(ses_item_list),
        "item_list":item_list(hinban,color,size,place,modal_type,check_0_ses)
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
            "hontai_num":hontai,
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
    if rows[0]=="品番,商品名,カラー,カラーコード,サイズ,サイズコード,数量,見積番号,SKU,納入先,入荷予定日,発送伝票備考,加工発注番号-バージョン,商品発注番号\r" or \
        rows[0]=="品番,商品名（商品名＋カラー＋サイズ）,カラー,カラーコード,サイズ,サイズコード,数量,見積番号,JAN,納入先,入荷予定日\r":
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
    modal_type=request.POST.get("modal_type")
    if modal_type=="zaiko":
        ses_item_list=request.session["zaiko"]["items"]
        ses_item_list.remove(hontai_kazu)
        request.session["zaiko"]["items"]=ses_item_list
    else:
        ses_item_list=request.session["zaiko"]["items2"]
        ses_item_list.remove(hontai_kazu)
        request.session["zaiko"]["items2"]=ses_item_list

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

    # 拠点で分割
    items=request.session["zaiko"]["items"]
    place_list=[]
    for i in items:
        hontai_num,kazu=map(int,i.split("_"))
        ins=Shouhin.objects.get(hontai_num=hontai_num)
        place_list.append(ins.place)
    place_list=set(place_list)

    for i in place_list:
        ####### Irai_list #######
        if irai_type in ["zaiko","catalog"]:
            if dic["btn_t1"]=="regular":
                hassou_type=1
            else:
                hassou_type=2

        # 在庫出荷
        if irai_type=="zaiko":
            if dic["btn_t2"]=="kakou":
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
                    bikou=dic["bikou"],
                    place=i,
                )
            elif dic["btn_t2"]=="muji":
                Irai_list.objects.create(
                    irai_num=irai_num,
                    shozoku=dic["shozoku"],
                    tantou=dic["tantou"],
                    irai_type=0,
                    hassou_type=hassou_type,
                    hassou_day=dic["btn_t1_day"],
                    zaiko_type=dic["btn_t2"],
                    zaiko_cus=dic["cus"],
                    zaiko_system=dic["system"],
                    bikou=dic["bikou"],
                    place=i,
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
                place=i,
            )
        # カタログ発送
        elif irai_type=="catalog":
            if dic["btn_t2"]=="tempo":
                Irai_list.objects.create(
                    irai_num=irai_num,
                    shozoku=dic["shozoku"],
                    tantou=dic["tantou"],
                    irai_type=2,
                    hassou_type=hassou_type,
                    hassou_day=dic["btn_t1_day"],
                    catalog_type=dic["btn_t2"],
                    catalog_tempo=dic["tempo"],
                    bikou=dic["bikou"],
                    place=i,
                )
            elif dic["btn_t2"]=="cus":
                Irai_list.objects.create(
                    irai_num=irai_num,
                    shozoku=dic["shozoku"],
                    tantou=dic["tantou"],
                    irai_type=2,
                    hassou_type=hassou_type,
                    hassou_day=dic["btn_t1_day"],
                    catalog_type=dic["btn_t2"],
                    catalog_cus_com=dic["cus_dic"]["cat_com"],
                    catalog_cus_name=dic["cus_dic"]["cat_name"],
                    catalog_cus_yubin=dic["cus_dic"]["cat_yubin"],
                    catalog_cus_pref=dic["cus_dic"]["cat_pref"],
                    catalog_cus_city=dic["cus_dic"]["cat_city"],
                    catalog_cus_banchi=dic["cus_dic"]["cat_banchi"],
                    catalog_cus_build=dic["cus_dic"]["cat_build"],
                    catalog_cus_tel=dic["cus_dic"]["cat_tel"],
                    catalog_cus_tel_search=dic["cus_dic"]["cat_tel"].replace("-","").strip(),
                    catalog_cus_mail=dic["cus_dic"]["cat_mail"],
                    bikou=dic["bikou"],
                    place=i,
                )

        ####### 商品 #######
        for h in items:
            hontai_num,kazu=map(int,h.split("_"))
            ins=Shouhin.objects.get(hontai_num=hontai_num)

            if ins.place==i:
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

    request.session["zaiko"]["items"]=[]
    pk_list=list(Irai_list.objects.filter(irai_num=irai_num).values_list("id",flat=True))

    d={"pk_list":pk_list}
    return JsonResponse(d)


# 依頼履歴_一覧
@login_required
def rireki_index(request):
    shozoku_list=list(Shozoku.objects.all().values_list("shozoku",flat=True))
    place_list=list(Place.objects.filter(show=1).values_list("place",flat=True))
    ses=request.session["zaiko"]["rireki_search"]

    # フィルター
    if len(ses)==0:
        irai_list=Irai_list.objects.all().order_by("irai_num").reverse()
    else:
        fil={}
        if ses["sr_irai_num"] != "":
            fil["irai_num"]=ses["sr_irai_num"]
        if ses["sr_irai_day_st"] != "":
            fil["irai_day__gte"]=ses["sr_irai_day_st"] + " 00:00:00"
        if ses["sr_irai_day_ed"] != "":
            fil["irai_day__lte"]=ses["sr_irai_day_ed"] + " 23:59:59"
        if ses["sr_hassou_day_st"] != "":
            fil["hassou_day__gte"]=ses["sr_hassou_day_st"]
        if ses["sr_hassou_day_ed"] != "":
            fil["hassou_day__lte"]=ses["sr_hassou_day_ed"]
        if ses["sr_hassou_type"] != "":
            fil["hassou_type"]=ses["sr_hassou_type"]
        if ses["sr_shozoku"] != "":
            fil["shozoku"]=ses["sr_shozoku"]
        if ses["sr_tantou"] != "":
            fil["tantou__contains"]=ses["sr_tantou"].strip()
        if ses["sr_naiyou_1"] != "":
            fil["irai_type"]=ses["sr_naiyou_1"]

        if ses["sr_naiyou_2"] != "":
            ins_zaiko=list(Irai_list.objects.filter(zaiko_type=ses["sr_naiyou_2"]).values_list("irai_num",flat=True))
            ins_catalog=list(Irai_list.objects.filter(catalog_type=ses["sr_naiyou_2"]).values_list("irai_num",flat=True))
            ins_all=set(ins_zaiko + ins_catalog)
            fil["irai_num__in"]=ins_all

        if ses["sr_place"] != "":
            fil["place"]=ses["sr_place"]
        if ses["sr_status"] != "":
            fil["irai_status"]=ses["sr_status"]

        if ses["sr_cus"] != "":
            ins_zaiko_cus=list(Irai_list.objects.filter(zaiko_cus__contains=ses["sr_cus"]).values_list("irai_num",flat=True))
            ins_zaiko_kakouba=list(Irai_list.objects.filter(zaiko_kakouba__contains=ses["sr_cus"]).values_list("irai_num",flat=True))
            ins_zaiko_gara=list(Irai_list.objects.filter(zaiko_gara__contains=ses["sr_cus"]).values_list("irai_num",flat=True))
            ins_keep_cus=list(Irai_list.objects.filter(keep_cus__contains=ses["sr_cus"]).values_list("irai_num",flat=True))
            ins_catalog_cus_com=list(Irai_list.objects.filter(catalog_cus_com__contains=ses["sr_cus"]).values_list("irai_num",flat=True))
            ins_catalog_cus_name=list(Irai_list.objects.filter(catalog_cus_name__contains=ses["sr_cus"]).values_list("irai_num",flat=True))
            ins_catalog_tempo=list(Irai_list.objects.filter(catalog_tempo__contains=ses["sr_cus"]).values_list("irai_num",flat=True))
            ins_all=set(ins_zaiko_cus + ins_zaiko_kakouba + ins_zaiko_gara + ins_keep_cus + ins_catalog_cus_com + ins_catalog_cus_name + ins_catalog_tempo)
            fil["irai_num__in"]=ins_all

        if ses["sr_tel"] != "":
            fil["catalog_cus_tel"]=ses["sr_tel"].strip().replace("-","") 
        if ses["sr_mail"] != "":          
            fil["catalog_cus_mail"]=ses["sr_mail"]

        irai_list=Irai_list.objects.filter(**fil).order_by("irai_num").reverse()

    sr_hassou_type={"1":"通常便","2":"お急ぎ便","3":"当日出荷"}
    sr_naiyou_1={"0":"商品在庫発送","1":"キープ","2":"資材・カタログ発送","3":"入庫"}
    sr_naiyou_2_zaiko={"kakou":"加工あり","muji":"無地"}
    sr_naiyou_2_catalog={"tempo":"店舗あて","cus":"顧客あて"}
    sr_status={"0":"発送待ち","2":"発送済み","1":"キープ中","4":"キープ解除","3":"キャンセル","6":"準備中"}
    

    #全ページ数
    if irai_list.count()==0:
        all_num=1
    elif irai_list.count() % 30== 0:
        all_num=irai_list.count() / 30
    else:
        all_num=irai_list.count() // 30 + 1
    all_num=int(all_num)
    request.session["zaiko"]["all_page_num"]=all_num
    num=request.session["zaiko"]["page_num"]
    irai_list=irai_list[(num-1)*30 : num*30]

    request.session["zaiko"]["now_page"]="一覧"
    params={
        "irai_list":irai_list,
        "shozoku_list":shozoku_list,
        "place_list":place_list,
        "sr_hassou_type":sr_hassou_type,
        "sr_naiyou_1":sr_naiyou_1,
        "sr_naiyou_2_zaiko":sr_naiyou_2_zaiko,
        "sr_naiyou_2_catalog":sr_naiyou_2_catalog,
        "sr_status":sr_status,
        "num":num,
        "all_num":all_num,
        "ses":ses,
    }
    return render(request,"zaiko/rireki_list.html",params)


# 履歴一覧_検索
def rireki_search(request):
    form_data = {key: value for key, value in request.POST.items()}
    request.session["zaiko"]["rireki_search"]=form_data
    request.session["zaiko"]["page_num"]=1
    return redirect("zaiko:rireki_index")


# ページネーション_前へ
def page_prev(request):
    num=request.session["zaiko"]["page_num"]
    if num-1 > 0:
        request.session["zaiko"]["page_num"] = num - 1
    return redirect("zaiko:rireki_index")

# ページネーション_最初
def page_first(request):
    request.session["zaiko"]["page_num"] = 1
    return redirect("zaiko:rireki_index")

# ページネーション_次へ
def page_next(request):
    num=request.session["zaiko"]["page_num"]
    all_num=request.session["zaiko"]["all_page_num"]
    if num+1 <= all_num:
        request.session["zaiko"]["page_num"] = num + 1
    return redirect("zaiko:rireki_index")

# ページネーション_最後
def page_last(request):
    all_num=request.session["zaiko"]["all_page_num"]
    request.session["zaiko"]["page_num"]=all_num
    return redirect("zaiko:rireki_index")


# 依頼履歴_詳細
@login_required
def rireki_detail(request,pk):
    ins=Irai_list.objects.get(pk=pk)
    irai_num=ins.irai_num
    place=ins.place
    pk_count=Irai_list.objects.filter(irai_num=irai_num).count()

    request.session["zaiko"]["now_page"]="詳細"
    params={
        "irai":Irai_list.objects.filter(pk=pk).values()[0],
        "shouhin_list":Irai_detail.objects.filter(irai_num=irai_num,place=place).values(),
        "pk_count":pk_count,
    }
    return render(request,"zaiko/rireki_index.html",params)


# 当日出荷に変更
def irai_change_today(request):
    irai_num=request.POST.get("irai_num")
    place=request.POST.get("place")
    ins=Irai_list.objects.get(irai_num=irai_num,place=place)
    ins.hassou_type=3
    ins.hassou_day=datetime.today()
    ins.save()
    d={}
    return JsonResponse(d)


# 依頼キャンセル
def irai_cancel(request):
    irai_num=request.POST.get("irai_num")
    place=request.POST.get("place")
    name=request.POST.get("name")
    ins=Irai_list.objects.get(irai_num=irai_num,place=place)
    ins.irai_status=3
    ins.cancel_day=name + "：" + datetime.now().strftime("%Y年%m月%d日 %H:%M")
    ins.save()

    # 在庫を戻す
    shouhin_list=Irai_detail.objects.filter(irai_num=irai_num)
    for i in shouhin_list:
        ins2=Shouhin.objects.get(hontai_num=i.hontai_num)
        if ins.irai_type in [0,2]:
            ins2.available += i.kazu
        elif ins.irai_type==1:
            ins2.available += i.kazu
            ins2.keep -= i.kazu
        ins2.save()

    d={}
    return JsonResponse(d)


# 発送待ちに戻す
def irai_reset(request):
    irai_num=request.POST.get("irai_num")
    place=request.POST.get("place")
    ins=Irai_list.objects.get(irai_num=irai_num,place=place)
    ins.irai_status=0
    ins.save()
    d={}
    return JsonResponse(d)


# キープから発送
def irai_keep_hassou(request):
    irai_num=request.POST.get("irai_num")
    place=request.POST.get("place")
    ins=Irai_list.objects.get(irai_num=irai_num,place=place)
    ins.irai_status=3
    ins.cancel_day="発送切替：" + datetime.now().strftime("%Y年%m月%d日 %H:%M")
    ins.save()

    # キャンセル扱いにして、在庫を戻す
    shouhin_list=Irai_detail.objects.filter(irai_num=irai_num,place=place)
    ses_item=[]
    for i in shouhin_list:
        ins2=Shouhin.objects.get(hontai_num=i.hontai_num)
        ins2.available += i.kazu
        ins2.keep -= i.kazu
        ins2.save()
        ses_item.append(str(i.hontai_num) + "_" + str(i.kazu))
    request.session["zaiko"]["items"]=ses_item
    d={}
    return JsonResponse(d)







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
    Size.objects.all().delete()

    # request.session.clear()  
    return redirect("zaiko:index")