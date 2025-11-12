# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def weekday_jp(value):
    """
    日付オブジェクトから日本語の曜日を返すフィルタ
    """
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    try:
        return weekdays[value.weekday()]
    except AttributeError:
        return ""