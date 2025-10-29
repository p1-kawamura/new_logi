from django.shortcuts import render,redirect
from .models import Shouhin,Place,Shozoku,Size
import io
import csv
import json
from django.http import JsonResponse
from datetime import datetime,timedelta
import os
from django.http import FileResponse
from django.conf import settings


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
    if "shozoku" not in request.session["zaiko"]:
        request.session["zaiko"]["shozoku"]=""
    if "tantou" not in request.session["zaiko"]:
        request.session["zaiko"]["tantou"]=""
    if "irai_type" not in request.session["zaiko"]:
        request.session["zaiko"]["irai_type"]=""
    if "irai_detail" not in request.session["zaiko"]:
        request.session["zaiko"]["irai_detail"]={}
    
    shozoku_list=Shozoku.objects.all()
    ses_item_list=request.session["zaiko"]["items"]
    order_list=order_item_list(ses_item_list)
    alert=0
    for i in order_list:
        if i["zaiko"]=="ng":
            alert += 1

    hassou_day=[
        "月曜日（" + next_weekday(0) + "）",
        "水曜日（" + next_weekday(2) + "）",
        "金曜日（" + next_weekday(4) + "）"
    ]

    params={
        "shozoku_list":shozoku_list,
        "order_list":order_list,
        "alert":alert,
        "hassou_day":hassou_day,
        }
    return render(request,"zaiko/index.html",params)


# FUNC 翌曜日取得
def next_weekday(target):
    today = datetime.today()
    days_ahead = (target - today.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7  # 今日が対象曜日なら次週を取得
    next_day = today + timedelta(days=days_ahead)
    return next_day.date().strftime("%m/%d")


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
    ses_item_list=request.session["zaiko"]["items"]

    d={"color_list":color_list,
       "size_list":size_list,
       "item_list":item_list(hinban,[],[],place),
       "place_list":place_list,
       "place":place,
       "ses_list":ses_list(ses_item_list)
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


# 依頼ボタン_キープ
def btn_irai_keep(request):
    keep_cus=request.POST.get("keep_cus")
    request.session["zaiko"]["irai_type"]=request.POST.get("irai_type")
    request.session["zaiko"]["irai_detail"]={"keep_cus":keep_cus}

    print(request.session["zaiko"]["irai_detail"])
    d={}
    return JsonResponse(d)







# 依頼送信_最終確認
def irai_send_check(request):
    ses_item_list=request.session["zaiko"]["items"]
    order_list=order_item_list(ses_item_list)
    alert=0
    for i in order_list:
        if i["zaiko"]=="ng":
            alert += 1

    d={"order_list":order_list,"alert":alert}
    return JsonResponse(d)


# 依頼送信_成功
def irai_send_ok(request):
    shozoku=request.POST.get("shozoku")
    tantou=request.POST.get("tantou")
    irai_type=request.POST.get("irai_type")
    form_dic=request.POST.get("form_dic")
    form_dic=json.loads(form_dic)
    bikou=request.POST.get("bikou")
    ses_item_list=request.session["zaiko"]["items"]

    print(shozoku,tantou,irai_type,form_dic,bikou)

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
    Shouhin.objects.all().delete()
    return redirect("zaiko:index")