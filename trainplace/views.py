# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http.response import Http404
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def get_trains_by_time_and_station(request):
    u"""
    時間(time=YYYY-MM-DD hh:mm)と駅名(station=XXXX)を受け取り、
    その時間の前後5分間に該当駅に滞在した車両の情報をJSON形式で返却する。
    該当車両が存在しなかった場合は空の配列が返却される。
    指定の駅名がDBに存在しなかった場合は Specified station not found のエラー。
    返却データは以下の形式となる。
    [{
        "time": "YYYY-MM-DD HH:mm:SS", #列車が該当駅に存在した時間
        "train_number": "A0010", #車両番号
        "train_type": "Local", #運行種別。LocalとかExpressとか
        "
    }, ...]
    ※該当駅に停車中のデータを取得出来ていない車両の扱い(ちょうど1分間隔のデータ更新時間内に停車、発車した場合)
    """
    # GETのみ受け付ける
    if request.method == "POST":
        raise Http404

    prm_time = request.GET.get('time', None)
    prm_st   = request.GET.get('station', None)

    if not prm_time or not prm_st:
        return HttpResponse("Required parameter not found. (time and station)", status=400)

    import dateutil.parser as dp
    import pytz
    try:
        time = dp.parse(prm_time).replace(tzinfo=pytz.timezone("Asia/Tokyo"))
    except:
        return HttpResponse("Time format is invalid. (require:YYYY-MM-DD hh:mm)", status=400)

