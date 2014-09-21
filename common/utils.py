# -*- coding: utf-8 -*-
import requests
import json
from django.conf import settings


def request_metro(prm):
    url = settings.METRO_EP + 'datapoints'
    response = requests.get(url, params=prm)
    return response


def create_prm(rdf_type):
    return  {"rdf:type":rdf_type, "acl:consumerKey":settings.METRO_TOKEN}

def parse_response(res):
    return json.loads(res.text)
