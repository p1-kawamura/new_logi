from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from zaiko.models import Shouhin,Size,Place,Irai_list,Irai_detail
import datetime
from django.http import JsonResponse
import io
import csv
import json
from django.db.models import Max
from zaiko.views import order_item_list
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django_pandas.io import read_frame
import openpyxl
from django.views.decorators.csrf import csrf_exempt


# 編集画面
def henshu_index(request):
    place_list=Place.objects.all()
    size_list=Size.objects.all()
    request.session["zaiko"]["now_page"]="編集"
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


# 商品テーブル_download
def henshu_excel_download(request):
    ins=Shouhin.objects.all()
    df=read_frame(ins)

    # Excelファイルをメモリ上に作成
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='商品一覧')

    buffer.seek(0)

    # HTTPレスポンスとしてExcelファイルを返す
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="products.xlsx"'
    return response


# サイズ画面
def size_index(request):
    sizes=Size.objects.all().order_by("size_num")
    request.session["zaiko"]["now_page"]="サイズ"
    return render(request,"zaiko2/size.html",{"sizes":sizes})


# サイズ番号（順番）
def size_num_func(request):
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


# 入庫画面
def nyuuko_index(request):
    ses_item_list=request.session["zaiko"]["items2"]
    order_list=order_item_list(ses_item_list)
    request.session["zaiko"]["now_page"]="入庫"
    return render(request,"zaiko2/nyuuko.html",{"order_list":order_list})


# 入庫用エクセル_download
def excel_download(request):
    ins=Shouhin.objects.all()
    df=read_frame(ins)
    df=df[["hontai_num","place","shouhin_num","shouhin_name","color","size"]]
    df["stocking"]=0

    # Excelファイルをメモリ上に作成
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='入庫専用')

    buffer.seek(0)

    # HTTPレスポンスとしてExcelファイルを返す
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="stocking.xlsx"'
    return response


# 入庫用エクセル_import
def excel_import(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb.active
        ses_item_list=request.session["zaiko"]["items2"]

        # 2行目からデータを読み込む（1行目はヘッダー）
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[6]>0:
                ses_item_list.append(str(row[0]) + "_" + str(row[6]))
        request.session["zaiko"]["items2"]=ses_item_list
            
    return redirect("zaiko2:nyuuko_index")


# 入庫処理
def nyuuko_send(request):
    tantou=request.POST.get("tantou")
    ses_item_list=request.session["zaiko"]["items2"]
    if len(ses_item_list)==0:
        ans="no"
    else:
        ans="yes"
        try:
            irai_num=Irai_list.objects.all().aggregate(Max("irai_num"))["irai_num__max"] + 1
        except:
            irai_num=1
        
        ####### Irai_list #######
        Irai_list.objects.create(
            irai_num=irai_num,
            shozoku="物流センター",
            tantou=tantou,
            irai_type=3,
            irai_status=5,
        )

        ####### 商品 #######
        for i in ses_item_list:
            hontai,kazu=map(int,i.split("_"))
            ins=Shouhin.objects.get(hontai_num=hontai)

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
            ins.available += kazu
            ins.stock += kazu
            ins.save()
        request.session["zaiko"]["items2"]=[]

    d={"ans":ans}
    return JsonResponse(d)


# VBA_依頼情報取得POST
@csrf_exempt
def vba_irai_list(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            hassou_type = data.get("hassou_type")
            place = data.get("place")
            
            if hassou_type=="当日":
                ins_lis=Irai_list.objects.filter(irai_status=0,hassou_type=3,place=place)
            elif hassou_type=="全部":
                ins_lis=Irai_list.objects.filter(irai_status=0,place=place)

            # 在庫関連
            irai_num_list=list(ins_lis.values_list("irai_num",flat=True))
            ins_det=Irai_detail.objects.filter(irai_num__in=irai_num_list,place=place)
            res_dic={
                "list":list(ins_lis.values()),
                "detail":list(ins_det.values()),
                }
            
            # 準備中に変更
            for i in ins_lis:
                i.irai_status=6
                i.save()

            return JsonResponse(res_dic,status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "POST only"}, status=405)


# VBA_発送完了POST
@csrf_exempt
def vba_hassou_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            hassou_data = data.get("hassou_data")
            place = data.get("place")

            # 発送完了に変更
            for i in hassou_data:
                ins=Irai_list.objects.get(irai_num=i["irai_num"],place=place)
                ins.irai_status=2
                ins.shipped_day=datetime.datetime.strptime(i["shipped_day"], "%Y/%m/%d").strftime("%Y-%m-%d")
                ins.shipped_com=i["shipped_com"]
                ins.shipped_num=i["shipped_num"]
                ins.save()

                # 在庫を減らす
                ins_det=Irai_detail.objects.filter(irai_num=i["irai_num"])
                for h in ins_det:
                    ins_sho=Shouhin.objects.get(hontai_num=h.hontai_num)
                    ins_sho.stock-=h.kazu
                    ins_sho.save()

            res_dic={}
            return JsonResponse(res_dic,status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "POST only"}, status=405)
    