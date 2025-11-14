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
    shozoku=models.CharField("所属",max_length=255,null=True,blank=True)
    tantou=models.CharField("担当者",max_length=255,null=True,blank=True)
    irai_type=models.IntegerField("依頼内容",default=0)
    irai_status=models.IntegerField("状態",default=0)
    hassou_type=models.IntegerField("発送タイプ",default=0)
    hassou_day=models.DateField("発送日",null=True,blank=True,default=None)
    zaiko_type=models.CharField("在庫出荷_商品",max_length=255,null=True,blank=True)
    zaiko_kakouba=models.CharField("在庫出荷_加工場/店舗",max_length=255,null=True,blank=True)
    zaiko_gara=models.CharField("在庫出荷_柄名",max_length=255,null=True,blank=True)
    zaiko_cus=models.CharField("在庫出荷_顧客名",max_length=255,null=True,blank=True)
    zaiko_system=models.CharField("在庫出荷_システム発送日",max_length=255,null=True,blank=True)
    keep_cus=models.CharField("キープ_顧客名",max_length=255,null=True,blank=True)
    catalog_type=models.CharField("カタログ_発送先",max_length=255,null=True,blank=True)
    catalog_tempo=models.CharField("カタログ_店舗名",max_length=255,null=True,blank=True)
    catalog_cus_com=models.CharField("カタログ_会社名",max_length=255,null=True,blank=True)
    catalog_cus_name=models.CharField("カタログ_氏名",max_length=255,null=True,blank=True)
    catalog_cus_yubin=models.CharField("カタログ_郵便番号",max_length=255,null=True,blank=True)
    catalog_cus_pref=models.CharField("カタログ_都道府県",max_length=255,null=True,blank=True)
    catalog_cus_city=models.CharField("カタログ_市区町村",max_length=255,null=True,blank=True)
    catalog_cus_banchi=models.CharField("カタログ_番地",max_length=255,null=True,blank=True)
    catalog_cus_build=models.CharField("カタログ_建物名",max_length=255,null=True,blank=True)
    catalog_cus_tel=models.CharField("カタログ_電話番号",max_length=255,null=True,blank=True)
    catalog_cus_tel_search=models.CharField("カタログ_電話番号_検索用",max_length=255,null=True,blank=True)
    catalog_cus_mail=models.CharField("カタログ_メールアドレス",max_length=255,null=True,blank=True)
    bikou=models.TextField("連絡事項",null=True,blank=True)
    shipped_day=models.DateField("発送完了日",null=True,blank=True,default=None)
    shipped_com=models.CharField("運送会社",max_length=255,null=True,blank=True)
    shipped_num=models.CharField("お問い合わせ番号",max_length=255,null=True,blank=True)
    cancel_day=models.CharField("キャンセル日時",max_length=255,null=True,blank=True)
    
    def __str__(self):
        return str(self.irai_num)
    
    # irai_type（依頼内容）　0:在庫出荷　1:キープ　2:カタログ発送　3:入庫
    # irai_status（状態）　0:発送待ち　1:キープ中　2:発送済　3:キャンセル　4:キープ解除　5:入庫済　6:準備中
    # hassou_type（発送タイプ）　0:なし（キープ/入庫） 1:通常便　2:お急ぎ便　3:当日出荷
    

class Irai_detail(models.Model):
    irai_num=models.IntegerField("依頼No",default=0)
    hontai_num=models.IntegerField("本体No",default=0)
    place=models.CharField("拠点",max_length=255)
    shouhin_num=models.CharField("品番",max_length=255)
    shouhin_name=models.CharField("品名",max_length=255,blank=True,null=True)
    color=models.CharField("カラー",max_length=255,blank=True,null=True)
    size=models.CharField("サイズ",max_length=255)
    size_num=models.IntegerField("サイズ値",default=0)
    tana=models.CharField("棚番",max_length=255,blank=True,null=True)
    cost_price=models.IntegerField("原価",default=0)
    bikou=models.CharField("備考",max_length=255,blank=True,null=True)
    attention=models.CharField("注意事項",max_length=255,blank=True,null=True)
    jan_code=models.CharField("JANコード",max_length=255,blank=True,null=True)
    kazu=models.IntegerField("数量",default=0)

    def __str__(self):
        return str(self.irai_num)
