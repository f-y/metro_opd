# -*- coding: utf-8 -*-
from django.db import models
from common.models import BaseModel
from common.utils import create_prm, request_metro, parse_response
from station.models import Station

import dateutil.parser as dp

class Railway(BaseModel):
    same_as = models.CharField(max_length=128, unique=True)
    date  = models.DateTimeField()
    title = models.CharField(max_length=256)
    region = models.CharField(max_length=1024, null=True, blank=True)
    operator = models.CharField(max_length=256, null=True, blank=True, verbose_name=u'運行会社')
    line_code = models.CharField(max_length=32, null=True, blank=True)


    def __unicode__(self):
        return u"%s" % (self.title)

    RDF_TYPE = "odpt:Railway"
    @classmethod
    def import_all(cls):
        cls.objects.all().delete()

        prm = create_prm(cls.RDF_TYPE)
        res = request_metro(prm)
        data  = parse_response(res)
        
        for d in data:
            try:
                date = dp.parse(d['dc:date'])

                rw = cls(ld_context   = d['@context'],
                    ld_id        = d['@id'],
                    ld_type      = d['@type'],
                    same_as      = d['owl:sameAs'],
                    date         = date,
                    title        = d['dc:title'],
                    operator     = d['odpt:operator'],
                    line_code = d['odpt:lineCode'],
                    region       = d['ug:region']
                    )
                rw.save()

                # save StationOrder
                so_list = d['odpt:stationOrder']
                for so in so_list:
                    st = Station.get_or_create(so['odpt:station'])
                    StationOrder.get_or_create(rw, st, so['odpt:index'])
                # save TravelTime 
                tt_list = d['odpt:travelTime']
                for tt in tt_list:
                    fs = Station.get_or_create(tt['odpt:fromStation'])
                    ts = Station.get_or_create(tt['odpt:toStation'])
                    TravelTime.get_or_create(rw, fs, ts, tt['odpt:necessaryTime'], tt['odpt:trainType'])
                # save WomenOnlyCar 
                if 'odpt:womenOnlyCar' in d:
                    woc_list = d['odpt:womenOnlyCar']
                    for woc in woc_list:
                        fs = Station.get_or_create(woc['odpt:fromStation'])
                        ts = Station.get_or_create(woc['odpt:toStation'])
                        time_from = dp.parse(woc['odpt:availableTimeFrom']).time()
                        time_until = dp.parse(woc['odpt:availableTimeUntil']).time()
                        WomenOnlyCar.get_or_create(rw, fs, ts, woc['odpt:operationDay'], time_from, time_until,
                                woc['odpt:carComposition'], woc['odpt:carNumber'])
            except:
                print d
                raise

        
                
    @classmethod
    def get_by_id(cls, same_as):
        if cls.objects.filter(same_as=same_as).exists():
            return cls.objects.get(same_as=same_as)
        else:
            return None



class StationOrder(BaseModel):
    railway = models.ForeignKey(Railway)
    station = models.ForeignKey(Station)
    index = models.IntegerField()

    class Meta:
        unique_together = ('railway', 'station')

    def __unicode__(self):
        return u'%s: %s' % (self.index, self.station,)

    @classmethod
    def get_or_create(cls, railway, station, index):
        if cls.objects.filter(railway=railway, station=station).exists():
            od = cls.objects.get(railway=railway, station=station)
            od.index = index # 最新に更新する
            od.save()
            return od
        od = cls(railway=railway, station=station, index=index)
        od.save()
        return od

class TravelTime(BaseModel):
    railway = models.ForeignKey(Railway)
    from_station = models.ForeignKey(Station, related_name='%(class)s_fromstations')
    to_station = models.ForeignKey(Station, related_name='%(class)s_tostations')
    necessary_time = models.IntegerField()
    train_type = models.CharField(max_length=256)

    class Meta:
        unique_together = ('railway', 'from_station', 'to_station')

    def __unicode__(self):
        return u'%s %s - %s : %s 分' % (self.railway, self.from_station, self.to_station, self.necessary_time)

    @classmethod
    def get_or_create(cls, railway, from_station, to_station, necessary_time, train_type):
        if cls.objects.filter(railway=railway, from_station=from_station, to_station=to_station).exists():
            tt = cls.objects.get(railway=railway, from_station=from_station, to_station=to_station)
            # 最新の値に更新
            tt.necessary_time = necessary_time
            tt.train_type = train_type
            tt.save()
            return tt
        tt = cls(railway=railway, from_station=from_station, to_station=to_station,
                necessary_time=necessary_time, train_type=train_type)
        tt.save()
        return tt


class WomenOnlyCar(BaseModel):
    railway = models.ForeignKey(Railway)
    from_station = models.ForeignKey(Station, related_name='%(class)s_fromstations')
    to_station = models.ForeignKey(Station, related_name='%(class)s_tostations')
    operation_day = models.CharField(max_length=40)
    available_time_from = models.TimeField()
    available_time_until = models.TimeField()
    car_composition = models.IntegerField(verbose_name=u'車両編成数')
    car_number = models.IntegerField(verbose_name=u'実施車両号車番号')

    class Meta:
        unique_together = ('railway', 'from_station', 'to_station')

    def __unicode__(self):
        return u'%s %s - %s: %s ~ %s (%s)' % (self.railway, self.from_station, self.to_station, 
                self.available_time_from, self.available_time_until, self.operation_day)

    @classmethod
    def get_or_create(cls, railway, from_station, to_station, operation_day, available_time_from, available_time_until, car_composition, car_number):
        if cls.objects.filter(railway=railway, from_station=from_station, to_station=to_station).exists():
            woc = cls.objects.get(railway=railway, from_station=from_station, to_station=to_station)
            # 最新の値に更新
            woc.operation_day = operation_day
            woc.available_time_from = available_time_from
            woc.available_time_until = available_time_until
            woc.car_composition = car_composition
            woc.car_number = car_number
            woc.save()
            return woc
        woc = cls(railway=railway, from_station=from_station, to_station=to_station,
                operation_day=operation_day, available_time_from=available_time_from, available_time_until=available_time_until,
                car_composition=car_composition, car_number=car_number)
        woc.save()
        return woc

