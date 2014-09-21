# -*- coding: utf-8 -*-
from django.db import models
from common.models import BaseModel
from common.utils import create_prm, request_metro, parse_response

import dateutil.parser as dp

class Station(BaseModel):
    same_as = models.CharField(max_length=127, unique=True)
    date  = models.DateTimeField()
    title = models.CharField(max_length=255)
    connecting_railways = models.CharField(max_length=1023, verbose_name=u'接続先路線情報')
    exits  = models.CharField(max_length=4091, null=True, blank=True, verbose_name=u'出口情報')
    facility = models.CharField(max_length=1023, verbose_name=u'施設情報ID')
    operator = models.CharField(max_length=255, verbose_name=u'運行会社')
    passenger_surveys = models.CharField(max_length=1023, verbose_name=u'駅情報')
    railway = models.CharField(max_length=255, verbose_name=u'路線情報')
    station_code = models.CharField(max_length=31)
    region = models.CharField(max_length=1023)


    def __unicode__(self):
        return "%s (%s)" % (self.title, self.same_as)

    RDF_TYPE = "odpt:Station"
    @classmethod
    def import_all(cls):
        cls.objects.all().delete()

        prm = create_prm(cls.RDF_TYPE)
        res = request_metro(prm)
        data  = parse_response(res)
        
        instances = []
        for d in data:
            try:
                date = dp.parse(d['dc:date'])
                conn_railways = ','.join(d['odpt:connectingRailway'])
                exits = ','.join(d['odpt:exit']) if d['odpt:exit'] else ''
                surveys = ','.join(d['odpt:passengerSurvey'])

                instances.append(
                cls(ld_context   = d['@context'],
                    ld_id        = d['@id'],
                    ld_type      = d['@type'],
                    same_as      = d['owl:sameAs'],
                    date         = date,
                    title        = d['dc:title'],
                    connecting_railways = conn_railways,
                    exits        = exits,
                    facility     = d['odpt:facility'],
                    operator     = d['odpt:operator'],
                    passenger_surveys = surveys,
                    railway      = d['odpt:railway'],
                    station_code = d['odpt:stationCode'],
                    region       = d['ug:region']
                    ))
            except:
                print d
                raise
        for ins in instances : ins.save()
                
    @classmethod
    def get_by_id(cls, same_as):
        if cls.objects.filter(same_as=same_as).exists():
            return cls.objects.get(same_as=same_as)
        else:
            return None

