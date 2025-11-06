from django.db import models

class Shouhin(models.Model):
    hontai_num=models.IntegerField("本体No",primary_key=True)
    place=models.CharField("拠点",max_length=255)
    shouhin_num=models.CharField("品番",max_length=255)
    shouhin_name=models.CharField("品名",max_length=255,blank=True,null=True)
    shouhin_set=models.CharField("品番 + 品名",max_length=255,blank=True,null=True)
    color=models.CharField("カラー",max_length=255,blank=True,null=True)
    size=models.CharField("サイズ",max_length=255)
    size_num=models.IntegerField("サイズ値",default=0)
    available=models.IntegerField("発注可能数",default=0)
    keep=models.IntegerField("キープ数",default=0)
    stock=models.IntegerField("在庫数",default=0)
    tana=models.CharField("棚番",max_length=255,blank=True,null=True)
    cost_price=models.IntegerField("原価",default=0)
    bikou=models.CharField("備考",max_length=255,blank=True,null=True)
    attention=models.CharField("注意事項",max_length=255,blank=True,null=True)
    create_day=models.CharField("登録日",max_length=255,blank=True,null=True)
    jan_code=models.CharField("JANコード",max_length=255,blank=True,null=True)
    sys_stock=models.IntegerField("システム在庫",default=0)
    sys_order=models.IntegerField("システム発注",default=0)

    def __str__(self):
        return str(self.hontai_num)
    
    # sys_stock（システム在庫）　0:なし　1:連動
    # sys_order（システム発注）　0:なし　1:連動


class Place(models.Model):
    place=models.CharField("拠点",max_length=255)
    show=models.IntegerField("営業に表示",default=0)

    def __str__(self):
        return self.place
    
    # show（営業に表示）　0:しない　1:表示


class Shozoku(models.Model):
    shozoku=models.CharField("所属",max_length=30)

    def __str__(self):
        return self.shozoku
    

class Size(models.Model):
    size_num=models.IntegerField("順番",null=False)
    size=models.CharField("サイズ",max_length=255,blank=True)

    def __str__(self):
        return self.size
    

class Irai_list(models.Model):
    irai_num=models.IntegerField("依頼No",primary_key=True)
    irai_day=models.DateTimeField("依頼日",auto_now_add=True)
    shozoku=models.CharField("所属",max_length=255,blank=True)
    tantou=models.CharField("担当者",max_length=255,blank=True)
    irai_type=models.IntegerField("依頼内容",default=0)
    hassou_type=models.IntegerField("発送タイプ",default=0)
    hassou_day=models.DateField("発送日",null=True,default=None)


    def __str__(self):
        return str(self.irai_num)
    
    # irai_type（依頼内容）　0:在庫出荷　1:キープ　2:カタログ発送
    # hassou_type（発送日タイプ）　0:なし（キープ） 1:通常便　2:お急ぎ便　3:当日発送

    