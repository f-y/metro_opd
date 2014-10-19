# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, Http404
import json

from station.models import Station

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_station_list(request):

    if request.method == "POST":
        return Http404

    js = {}
    js['stations'] = [st.to_json() for st in Station.get_metro_stations()]
    return HttpResponse(json.dumps(js), content_type='application/json')

