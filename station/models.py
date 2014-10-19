# -*- coding: utf-8 -*-
from django.db import models
from common.models import BaseModel
from common.utils import create_prm, request_metro, parse_response

import dateutil.parser as dp

class Station(BaseModel):
    same_as = models.CharField(max_length=127, unique=True)
    date  = models.DateTimeField()
    title = models.CharField(max_length=255)
    connecting_railways = models.CharField(max_length=1023, null=True, blank=True, verbose_name=u'接続先路線情報')
    exits  = models.CharField(max_length=4091, null=True, blank=True, verbose_name=u'出口情報')
    facility = models.CharField(max_length=1023, null=True, blank=True, verbose_name=u'施設情報ID')
    operator = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'運行会社')
    passenger_surveys = models.CharField(max_length=1023, null=True, blank=True, verbose_name=u'駅情報')
    railway_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'路線情報')
    station_code = models.CharField(max_length=31, null=True, blank=True)
    region = models.CharField(max_length=1023, null=True, blank=True)

    class Meta:
        ordering = ['railway_id']

    @property
    def railway(self):
        import railway
        railway = railway.models.Railway.get_by_id(self.railway_id)
        if railway:
            return railway
        else:
            return None

    def __unicode__(self):
        if self.railway:
            return u"%s線 %s" % (self.railway, self.title)
        else:
            return u"%s" % (self.title, )

    def to_json(self):
        obj = {}
        obj['title'] = self.title
        if self.railway:
            obj['railway'] = self.railway.title
        return obj

    @classmethod
    def get_metro_stations(cls):
        return cls.objects.filter(station_code__isnull=False)

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
                    railway_id      = d['odpt:railway'],
                    station_code = d['odpt:stationCode'],
                    region       = d['ug:region']
                    ))
            except:
                print d
                raise
        for ins in instances : ins.save()

    @classmethod
    def get_or_create(cls, same_as):
        if not same_as:
            return None
        st = cls.get_by_id(same_as)
        if st:
            return st
        import datetime
        import pytz
        st = cls(ld_context   = 'http://vocab.tokyometroapp.jp/context_odpt_Station.jsonld',
            ld_id        = 'urn:ucode:none',
            ld_type      = 'odpt.Station',
            same_as      = same_as,
            date         = datetime.datetime.now().replace(tzinfo=pytz.UTC),
            title        = same_as[same_as.rindex('.')+1:],
            connecting_railways = None,
            exits        = None,
            facility     = None,
            operator     = None,
            passenger_surveys = None,
            railway_id   = None,
            station_code = None,
            region       = None
            )
        st.save()
        return st
        
                
    @classmethod
    def get_by_id(cls, same_as):
        if cls.objects.filter(same_as=same_as).exists():
            return cls.objects.get(same_as=same_as)
        else:
            return None

